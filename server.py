#!flask/bin/python
import binascii
import json
import os
import re

import psycopg2
from flask import Flask, jsonify, abort, request, make_response, url_for, render_template, redirect, session
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__, static_url_path="", static_folder="static")
app.secret_key = binascii.hexlify(os.urandom(12)).decode('utf-8')
auth = HTTPBasicAuth()


@auth.get_password
def get_password(username):
    SQL = "SELECT password FROM users WHERE username='{}'".format(username)
    curr.execute(SQL)
    fetched = curr.fetchone()
    if fetched is not None:
        password = fetched[0]
    else:
        password = None

    if password is not None:
        return password
    else:
        return None


@auth.error_handler
def unauthorized():
    return make_response(jsonify({'error': 'Unauthorized access'}), 403)
    # return 403 instead of 401 to prevent browsers from displaying the default auth dialog


@app.errorhandler(400)
def not_found():
    return make_response(jsonify({'error': 'Bad request'}), 404)


@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'Not found'}), 404)


# take quote randomly
def get_quote_random():
    SQL = "SELECT quote,writer FROM quotes,writers,categories WHERE (quotes.writer_id = writers.id) AND \
            (quotes.category_id = categories.id) AND (categories.keyword NOT IN ('notfound')) ORDER BY random() LIMIT 1"
    curr.execute(SQL)
    quote = curr.fetchone()
    return quote


# take quote with keyword
def get_quote_with_keyword(keyword):
    SQL = "SELECT EXISTS (SELECT 1 FROM categories,quotes WHERE (quotes.category_id = categories.id) AND (keyword = '{}'))".format(
        keyword)
    curr.execute(SQL)
    category_exists = curr.fetchone()[0]

    if not category_exists:
        keyword = "notfound"
        session['404'] = True
    else:
        session['404'] = False

    SQL = "SELECT quotes.id,quote,writer FROM quotes,categories,writers WHERE (quotes.category_id = categories.id) AND \
          (quotes.writer_id = writers.id) AND (keyword = '{}') ORDER BY random() LIMIT 1".format(
        keyword)
    curr.execute(SQL)
    quote = curr.fetchone()
    return quote


@app.route('/quote/api/v1.0/random', methods=['GET'])
@auth.login_required
def get_random():
    quote = get_quote_random()
    if 'ApiKey' not in request.headers:
        return make_response(jsonify({'error': 'Add ApiKey to header'}), 400)
    api_key = request.headers['ApiKey']
    api_key_exist_in_db = False
    SQL = "SELECT id from users WHERE api_key='{}'".format(api_key)

    if api_key != "":
        curr.execute(SQL)
        if curr.fetchone() is not None: api_key_exist_in_db = True

    if api_key == "" or not api_key_exist_in_db:
        return make_response(jsonify({'error': 'ApiKey Missing or Wrong'}), 400)
    else:
        return jsonify({
            'quote': quote[1],
            'writer': quote[2]
        })


@app.route('/quote/api/v1.0/<string:keyword>', methods=['GET'])
@auth.login_required
def get_with_keyword(keyword):
    quote = get_quote_with_keyword(keyword=keyword)

    if 'ApiKey' not in request.headers:
        return make_response(jsonify({'error': 'Add ApiKey to header'}), 400)
    api_key = request.headers['ApiKey']
    api_key_exist_in_db = False
    SQL = "SELECT id from users WHERE api_key='{}'".format(api_key)

    if api_key != "":
        curr.execute(SQL)
        if curr.fetchone() is not None: api_key_exist_in_db = True

    if api_key == "" or not api_key_exist_in_db:
        return make_response(jsonify({'error': 'ApiKey Missing or Wrong'}), 400)
    else:
        if len(quote) == 0:
            abort(404)
        return jsonify({
            'quote': quote[1],
            'writer': quote[2]
        })


@app.route('/', methods=['GET', 'POST'])
def keyword():
    keyword = ""
    if request.method == 'POST':
        keyword = request.form.get('keyword')
    elif request.method == 'GET':
        SQL = "SELECT keyword FROM categories WHERE (keyword NOT IN ('notfound'))ORDER BY random() LIMIT 1"
        curr.execute(SQL)
        keyword = curr.fetchone()[0]

    data = get_quote_with_keyword(keyword)
    is_hidden = ''
    is_logged = ''
    if session.get('404'):
        if session['404']:
            is_hidden = 'hidden'
        else:
            is_hidden = ''
    if session.get('user_logged'):
        is_logged = ''
    else:
        is_logged = 'hidden'
    return render_template('home.html', writer=data[2], quote=data[1], keyword_value=keyword, quote_id=data[0],
                           isHidden=is_hidden, islogged=is_logged)


@app.route('/random')
def home_page():
    data = get_quote_random()
    return render_template('random.html', writer=data[1], quote=data[0])


@app.route('/about')
def about_page():
    return render_template('about.html')


@app.route('/authentication', methods=['GET', 'POST'])
def auth_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if request.form['btn'] == 'Login':
            # do login
            SQL = "SELECT * FROM users WHERE username='{}'".format(username)
            curr.execute(SQL)
            user = curr.fetchone()

            if username == "" or password == "":
                return render_template('auth.html', prompt="Form field should be filled")
            elif user is None:
                return render_template('auth.html', prompt="Are you sure about that username?")
            else:
                if password == user[2]:
                    session['api_key'] = user[3]
                    session['username'] = user[1]
                    session['user_logged'] = True
                    return redirect(url_for('generateKey'))
                else:
                    return render_template('auth.html', prompt="Password invalid.")

        elif request.form['btn'] == 'Create':
            # do create
            if username == "":
                return render_template('auth.html', prompt="An user without name, are you robot?")
            elif password == "":
                return render_template('auth.html', prompt="Enter a pass, that might be helpful.")
            else:
                apikey = binascii.hexlify(os.urandom(12)).decode('utf-8')
                SQL = "INSERT INTO users (username, password, api_key) " \
                      "SELECT '{}', '{}', '{}' WHERE NOT EXISTS(SELECT id FROM users WHERE username='{}') RETURNING id;".format(
                    username, password, apikey, username)
                curr.execute(SQL)
                conn.commit()
                id = curr.fetchone()
                if id is not None:
                    session['api_key'] = apikey
                    session['user_logged'] = True
                    session['username'] = username
                    return redirect(url_for('generateKey'))
                else:
                    prompt = "Username '{}' exist, try another.".format(username)
                    return render_template('auth.html', prompt=prompt)

    elif request.method == 'GET':
        # if user logged in direct to generateKey
        if session.get('user_logged'):
            if session['user_logged']:
                return render_template('generateKey.html', apikey=session['api_key'])
        else:
            return render_template('auth.html')


@app.route('/generateKey')
def generateKey():
    # generate key and authentication
    return render_template('generateKey.html', apikey=session['api_key'])


@app.route('/logout')
def logout():
    session.pop('user_logged', None)
    session.pop('api_key', None)
    session.pop('username', None)
    return redirect(url_for('auth_page'))


@app.route('/giveRating', methods=['POST'])
def giveRating():
    star = request.form.get('rating')
    quote_id = request.form.get('quote_id')
    # keyword = request.form.get('keyword')
    SQL = "SELECT * FROM quotes WHERE id={}".format(quote_id)
    curr.execute(SQL)
    data = curr.fetchone()
    votes = data[2]
    rate = data[3]
    new_rate = 0
    if star == "star-5":
        new_rate = 5
    elif star == "star-4":
        new_rate = 4
    elif star == "star-3":
        new_rate = 3
    elif star == "star-2":
        new_rate = 2
    elif star == "star-1":
        new_rate = 1

    rate = float(rate * votes + new_rate) / float(votes + 1)
    votes = votes + 1

    SQL = "UPDATE quotes SET rate={}, votes={} WHERE id={}".format(rate, votes, quote_id)
    curr.execute(SQL)
    conn.commit()
    return jsonify({
        'status': 'OK',
        'rating': star
    })


@app.route('/feedback', methods=['POST'])
def feedback():
    comment = request.form.get('comment')
    quote_id = request.form.get('quote_id')
    username = session['username']

    SQL = "INSERT INTO comments(user_id, quote_id, comment) VALUES ( (SELECT id FROM users WHERE username='{}'), {}, '{}')".format(
        username, quote_id, comment)
    curr.execute(SQL)
    conn.commit()

    return jsonify({
        'status': 'OK'
    })


@app.route('/addNew', methods=['GET', 'POST'])
def addNew():
    SQL = "SELECT keyword FROM categories"
    curr.execute(SQL)
    categories = ''

    if session.get('user_logged'):
        prompt_hidden = "hidden"
        btn_hidden = ""
    else:
        prompt_hidden = ""
        btn_hidden = "hidden"
    for x in curr.fetchall():
        if x[0] != "notfound":
            categories += "<option value=" + "{}>".format(x[0]) + x[0] + "</option>"

    if request.method == "POST":
        quote = request.form.get('quote')
        writer = request.form.get('writer')
        keyword = request.form.get('sel1')
        if session.get('username'):
            username = session['username']
            # if user is admin he can directly add to the main quotes table
            if username == "admin":
                SQL = "SELECT id FROM writers WHERE writer = '{}'".format(writer)
                curr.execute(SQL)
                writer_id = curr.fetchone()

                SQL = "SELECT id from categories WHERE keyword = '{}'".format(keyword)
                curr.execute(SQL)
                category_id = curr.fetchone()[0]

                if writer_id:
                    # writer is in database
                    writer_id = writer_id[0]
                else:
                    # writer is not in database
                    # insert writer than return id
                    SQL = "INSERT INTO writers(writer) VALUES ('{}') RETURNING id".format(writer)
                    curr.execute(SQL)
                    conn.commit()
                    writer_id = curr.fetchone()[0]

                SQL = "INSERT INTO quotes(quote, category_id, writer_id) VALUES ('{}', {}, {})".format(quote,
                                                                                                       category_id,
                                                                                                       writer_id)

            else:
                SQL = "INSERT INTO user_quotes(user_id, quote, writer, category_id) VALUES  \
                  ((SELECT id FROM users WHERE username = '{}'),'{}','{}',(SELECT id FROM categories WHERE keyword = '{}'))".format(
                    username, quote, writer, keyword)

            curr.execute(SQL)
            conn.commit()

    return render_template("addNew.html", categoryList=categories, promptHidden=prompt_hidden, btnHidden=btn_hidden,
                           prompt='')


@app.route('/demo', methods=['GET', 'POST'])
def demo():
    DEMO_DIR = os.path.dirname(os.path.abspath(__file__)) + '/static/demo/'

    if request.method == 'POST':
        data = ''
        if request.form['btn'] == 'Create':
            path = os.path.join(DEMO_DIR, 'create.txt')
            with open(path) as f:
                read_data = f.read()
            try:
                curr.execute(read_data)
                conn.commit()
                data = "Tables created."
            except psycopg2.Error as e:
                data = e.diag.message_primary

        elif request.form['btn'] == 'Insert':
            path = os.path.join(DEMO_DIR, 'insert.txt')
            with open(path) as f:
                read_data = f.read()
            try:
                curr.execute(read_data)
                conn.commit()
                data = "Tables inserted."
            except psycopg2.Error as e:
                data = e.diag.message_primary

        elif request.form['btn'] == 'Update':
            path = os.path.join(DEMO_DIR, 'update.txt')
            with open(path) as f:
                read_data = f.read()
            try:
                curr.execute(read_data)
                conn.commit()
                data = "Update successful."
            except psycopg2.Error as e:
                data = e.diag.message_primary

        elif request.form['btn'] == 'Select':
            path = os.path.join(DEMO_DIR, 'select.txt')
            with open(path) as f:
                read_data = f.read()
            try:
                curr.execute(read_data)
                conn.commit()
                data = curr.fetchone()[1]
            except psycopg2.Error as e:
                data = e.diag.message_primary


        elif request.form['btn'] == 'Delete':
            path = os.path.join(DEMO_DIR, 'delete.txt')
            with open(path) as f:
                read_data = f.read()
            try:
                curr.execute(read_data)
                conn.commit()
                data = "All tables deleted."
            except psycopg2.Error as e:
                data = e.diag.message_primary

        return render_template("demo.html", result=data)
    elif request.method == 'GET':
        return render_template("demo.html", result='')


def get_elephantsql_dsn(vcap_services):
    """Returns the data source name for ElephantSQL."""
    parsed = json.loads(vcap_services)
    uri = parsed["elephantsql"][0]["credentials"]["uri"]
    match = re.match('postgres://(.*?):(.*?)@(.*?)(:(\d+))?/(.*)', uri)
    user, password, host, _, port, dbname = match.groups()
    dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format(user, password, host, port, dbname)
    return dsn


if __name__ == '__main__':
    VCAP_APP_PORT = os.getenv('VCAP_APP_PORT')
    if VCAP_APP_PORT is not None:
        port, debug = int(VCAP_APP_PORT), False
    else:
        port, debug = 5000, True

    VCAP_SERVICES = os.getenv('VCAP_SERVICES')
    if VCAP_SERVICES is not None:
        app.config['dsn'] = get_elephantsql_dsn(VCAP_SERVICES)
    else:
        dsn = """user='{}' password='{}' host='{}' port={}
             dbname='{}'""".format("", "", "localhost", 5432, "postgres")
        app.config['dsn'] = dsn

    conn = psycopg2.connect(app.config['dsn'])
    global curr
    curr = conn.cursor()

    app.run(host='0.0.0.0', port=int(port), debug=debug)

    conn.commit()
    conn.close()
