# KiloReader

KiloReader is a single-user feed reader. It's in a very early stage of
development, but the most basic functionality is working.

![screenshot](https://raw.github.com/tdryer/kiloreader/master/screenshot.png)

KiloReader consists of:

* server providing a REST API
 * written in Python
 * uses [Tornado](http://www.tornadoweb.org/) web server
 * uses [python-feedparser](http://pythonhosted.org/feedparser/) to download
 and parse feeds
 * uses [SQLAlchemy](http://www.sqlalchemy.org/) and
 [SQLite](http://www.sqlite.org/) to store feeds and entries
* web frontend for the API
 * written in Javascript
 * uses the [AngularJS](http://angularjs.org/) framework

## Usage

Doing the following in a virtualenv is recommended.

Python 2.7 is required. Install some extra dependencies which are required to
build the lxml package:

`sudo apt-get install python-dev libxslt1-dev libxml2-dev zlib1g-dev
build-essential`

Install KiloReader's requirements:

`pip install -r requirements.txt`

Run the functional tests:

`python -m backend.test.functional`

Currently the only way to use KiloReader is with the development server, which
requires installing [blackjid/tape](https://github.com/blackjid/tape) (outside
the virtualenv) to provide a simple reverse-proxy server.

Run the development server:

`./develop.sh`

Navigate to [http://localhost:8080](http://localhost:8080) to use the web
frontend.

## Major todos:

* periodic feed fetching while respecting cache headers
* nicer frontend that's optimized for mobile
* feed fetching in worker processes
* pagination support
* unit tests and better functional tests
* production deployment method with authentication
