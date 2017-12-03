User Guide
==========

Quote with Keyword
~~~~~~~~~~~~~~~~~~

In order to get a quote with given keyword, simply type the keyword in
the box and hit generate button. If the quote with given keyword exists
in database then result will be succesful. If there is no quote with
given keyword then rather showing a 404 error or not found error,
randomly choosen "404" quote will be displayed.

Below, there is an example of quote generating quote with keyword.

|itucsdb1741.png|

Rating
^^^^^^

After generating quote user can rate a quote if the given keyword is
related with the generated quote or they can give rating becuase they
like the quote. These rating data will be used later in order to
determine whether generated quote is good or not.

Randomly Choosen Quote
~~~~~~~~~~~~~~~~~~~~~~

If users don't have any particular keyword, still they can generate
quotes. This functionality can be reached from the menu.

|foto1.png|

API Service
~~~~~~~~~~~

Users who need a service for generating quotes, can be use this service.
In order to use this service they have to create an account using the
menu link. Afterwards, with the given API key they can generate thier
quotes either randomly or with given keyword.

API Usage
~~~~~~~~~


Before making a request user has to create credentials. In order to
that, **Auth** menu link should be used. After creating and user account
``API KEY`` will be given to user.

**Base Link**

``http://itucsdb1741.mybluemix.net/quote/api/v1.0/``

**Authentication**

Add following key-pairs to the Header. Basic Auth requires user to send
Username and Password.

::

    ApiKey = API_KEY_HERE 
    For Authorization use Basic Auth

**GET /quote/api/v1.0/random**

Below request will return randomly generated quote.

::

    GET /quote/api/v1.0/random HTTP/1.1
    Host: itucsdb1741.mybluemix.net
    ApiKey: API_KEY
    Authorization: Basic user-password

**GET /quote/api/v1.0/{?keyword}**

In order to get quote with keyword, it should be added at the and of
URL. In the example below quote with ``funny`` will be returned.

::

    GET /quote/api/v1.0/funny?ApiKey=API_KEY_HERE HTTP/1.1
    Authorization: Basic user-password
    ApiKey: API_KEY_HERE

**Error Codes and Meanings**

+------+-------------------------+-----------------------------------+
| Code | Text                    | Description                       |
+======+=========================+===================================+
| 400  | ApiKey Missing or Wrong | Api Key is wrong                  |
+------+-------------------------+-----------------------------------+
| 403  | Add ApiKey to header    | Api Key should be added to Header |
+------+-------------------------+-----------------------------------+
| 403  | Unauthorized access     | Basic Auth is missing in Header   |
+------+-------------------------+-----------------------------------+

.. |itucsdb1741.png| image:: https://s20.postimg.org/b5nya78od/itucsdb1741.png
.. |foto1.png| image:: https://s20.postimg.org/xet58e68d/foto1.png
