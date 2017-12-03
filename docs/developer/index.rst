Developer Guide
===============

Database Design
---------------

|eRdiagram.png|

The database includes six table. The 'users' table is for the users who want to use API service. The 'users' table holds the data for username, password and API key.

The 'categories' table holds the avaliable categories in the database at that time. The id variable is unique for each category.

The 'writers' table holds the name of the the writers and the id variable is unique for each one.

The 'quotes' table is the main table for database. It holds the value quotes, votes and rates also two foreign key for categories and writers.

The 'comments' table holds the data for comments sent by users. It has four rows, which are id as primary key, user_id for pointing out which user sent the comment,
quote_id for referencing for commented quote and finally comment itself.

The 'user_quotes' table holds the quotes which sent by user in order to be added to actual quotes database. These quotes should 
be examined by the admin and after they can be added to actual quote database manually.


Code
----

In order to built application below programming languages and libraries are used.

- Python 3.6.2
- PostgreSQL
- Flask


Since application both provides API service and user interface for web client, it can be analyzed with 3 part.

#. Web Client and backend
#. API service
#. Database

Web Client and backend
^^^^^^^^^^^^^^^^^^^^^^

..  code-block:: python
    def get_quote_random():
        SQL = "SELECT quote,writer FROM quotes,writers,categories WHERE (quotes.writer_id = writers.id) AND \
                (quotes.category_id = categories.id) AND (categories.keyword NOT IN ('notfound')) ORDER BY random() LIMIT 1"
        curr.execute(SQL)
        quote = curr.fetchone()
        return quote
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

The core of the applicaiton is served by these two function. These functions are called in ``home`` and ``random`` paths in order to generate quotes.
``get_quote_random()`` functions returns a randomly choosen quote from database. ``get_quote_with_keyword(keyword)`` function takes keyword as a parameter
and afterwards it checks whether keyword exists in database or not. If exists it creates a query with the keyword and returns data from database. If not
than a key is held in the session in order to specify that quote with the keyword is not exists in database. Also, it makes a quote request with keyword
``notfound``. This query returns one of the quotes which infrom users that given keyword is not exists.


..  code-block:: python
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


This code block executed when user reach the home page of the website. If it is the first time that user enters the site, since it is a GET request, function
will choose randomly keyword excluding ``notfound`` category. After that a quote with keyword will be generated. If user generating quotes with keyword using button
on the home page, then it will be a POST request. Because of this, rather than generating new keyword, keyword in the form field will be used. Also ``is_hidden`` and 
``is_logged`` session booleans are used for detecting whether user logged in or not. These way users will be prevented to send comments without logging in.


.. |eRdiagram.png| image:: https://s20.postimg.org/gtxk3wum5/erdiagram.png