[![GitHub code size in bytes](https://img.shields.io/github/languages/code-size/badges/shields.svg)](https://github.com/mhmmtucan/itucsdb1741) [![GitHub top language](https://img.shields.io/github/languages/top/badges/shields.svg)](https://github.com/mhmmtucan/itucsdb1741) [![GitHub license](https://img.shields.io/github/license/mhmmtucan/itucsdb1741.svg)](https://github.com/mhmmtucan/itucsdb1741/blob/master/LICENSE)

Generating quotes using keywords or randomly choosed.

This repo provides an API service for generating quotes with given keywords. If user dont want to give an keywords, then API provide him and randomly choosen quote. The number of qoutes are restricted by the quotes in database.

### Getting Started

Follow instuction below in order to setup applicaton.

* Download or clone repository.
* Start server, using `server.py` file. In order to start server use: `python3 server.py`

NOTE: In order to properly run the project database connection should be made.

### Usage

The demo of API service can be found [here](http://itucsdb1741.mybluemix.net/). 

[![itucsdb1741.png](https://s20.postimg.org/b5nya78od/itucsdb1741.png)](https://postimg.org/image/siy8p23zd/)

User can enter keyword in the search box and generate quotes.

### API Usage

Before making a request user has to create credentials. In order to that, **Auth** menu link should be used. After creating and user account `API KEY` will be given to user.

_**Base Link**_

`http://itucsdb1741.mybluemix.net/quote/api/v1.0/`

_**Authentication**_

Add following key-pairs to the Header. Basic Auth requires user to send Username and Password.

```
ApiKey = API_KEY_HERE 
For Authorization use Basic Auth
```

_**GET /quote/api/v1.0/random**_

Below request will return randomly generated quote.

```
GET /quote/api/v1.0/random HTTP/1.1
Host: itucsdb1741.mybluemix.net
ApiKey: API_KEY
Authorization: Basic user-password
```

_**GET /quote/api/v1.0/{?keyword}**_

In order to get quote with keyword, it should be added at the and of URL. In the example below quote with `funny` will be returned.

```
GET /quote/api/v1.0/funny?ApiKey=API_KEY_HERE HTTP/1.1
Authorization: Basic user-password
ApiKey: API_KEY_HERE
```

_**Error Codes and Meanings**_

| Code        | Text           | Description  |
| ------------- |:-------------:| -----:|
| 400           | ApiKey Missing or Wrong | Api Key is wrong |
| 403           | Add ApiKey to header      |   Api Key should be added to Header |
| 403           | Unauthorized access      |    Basic Auth is missing in Header |


### Builth With
* Python
* Flask
* Postgres
* Blumix-Cloud

### Licence
* GNU General Public License v3.0

### Version
* 1.0

