#!flask/bin/python
from flask import Flask, jsonify, abort, request, make_response, url_for, render_template, redirect, session
from flask_httpauth import HTTPBasicAuth
from random import randint
import psycopg2, os, binascii, re, json

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
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 404)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


# take quote randomly
def get_quote_random():
    curr.execute('SELECT count(*) AS exact_count FROM categories')
    size = curr.fetchone()[0]
    index = randint(1, size)
    SQL = "SELECT keyword FROM categories WHERE  id={}".format(index)
    curr.execute(SQL)
    keyword = curr.fetchone()[0]

    SQL = "SELECT count(*) AS exact_count FROM {}".format(keyword)
    curr.execute(SQL)
    size = curr.fetchone()[0]
    index = randint(1, size)
    SQL = "SELECT * FROM {} WHERE  id={}".format(keyword, index)
    curr.execute(SQL)
    quote = curr.fetchone()
    return quote


# take quote with keyword
def get_quote_with_keyword(keyword):
    SQL = "SELECT to_regclass('{}')".format(keyword)
    curr.execute(SQL)
    db_exists = curr.fetchone()[0]
    if db_exists is not None:
        SQL = "SELECT count(*) As exact_count FROM {}".format(keyword)
        curr.execute(SQL)
        size = curr.fetchone()[0]
        # keyword exist in database
        index = randint(1, size)
        SQL = "SELECT * FROM {} WHERE id={}".format(keyword, index)
        curr.execute(SQL)
        quote = curr.fetchone()
        return quote
    else:
        index = randint(1, 9)
        SQL = "SELECT * FROM notfound WHERE id={}".format(index)
        curr.execute(SQL)
        return ('0', curr.fetchone()[1], '404', '0', '0')


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
        curr.execute('SELECT count(*) AS exact_count FROM categories')
        size = curr.fetchone()[0]
        index = randint(1, size)
        SQL = "SELECT keyword FROM categories WHERE  id={}".format(index)
        curr.execute(SQL)
        keyword = curr.fetchone()[0]

    data = get_quote_with_keyword(keyword)
    return render_template('home.html', writer=data[2], quote=data[1], keyword_value=keyword, quote_id=data[0])


@app.route('/random')
def home_page():
    data = get_quote_random()
    return render_template('random.html', writer=data[2], quote=data[1])


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
    return redirect(url_for('auth_page'))


@app.route('/giveRating', methods=['POST'])
def giveRating():
    # TODO : 404 için rate i kapat
    star = request.form.get('rating')
    quote_id = request.form.get('quote_id')
    keyword = request.form.get('keyword')
    SQL = "SELECT * FROM {} WHERE id={}".format(keyword, quote_id)
    curr.execute(SQL)
    data = curr.fetchone()
    votes = data[3]
    rate = data[4]
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

    SQL = "UPDATE {} SET rate={}, votes={} WHERE id={}".format(keyword, rate, votes, quote_id)
    curr.execute(SQL)
    conn.commit()
    return jsonify({
        'status': 'OK',
        'rating': star
    })


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
        app.config['dsn'] = """user='vagrant' password='vagrant'
                                   host='localhost' port=5432 dbname='itucsdb'"""

    app.run(host='0.0.0.0', port=port, debug=debug)

    conn = psycopg2.connect(app.config['dsn'])
    global curr
    curr = conn.cursor()
    conn.commit()
    conn.close()
