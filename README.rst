``ptah_crowd`` README
==========================

This packages provides a nearly-complete user registration and management
facility.  It is similar to ``cartouche`` in feature set.  The `ptah_crowd` 
package contains:

- User registration forms

- Reset password functionality

- Ability to validate & suspend accounts

- User model

- User properties models/API

- Ptah Management Plugin so you can manipulate API in web interface

``ptah_crowd`` is built on-top of Pyramid and Ptah.  It provides quite a few
features and is generic enough to "plug into" instead of build from scratch.
It is a framework and not library.  ``ptah_crowd``` does something
out-of-the-box and is meant to be extended.  

It is worthwhile to understand that ``ptah_crowd`` is *not* a wsgi application.
You need an application such as one of the applications in the examples github
repository, https://github.com/ptahproject/examples

Quick start
-----------

If you do not have an application, lets use examples/ptah_models.

Install ``ptah_models`` into your virtualenv::

  $ cd examples/ptah_models
  $ /path/to/virtualenv/bin/python setup.py develop

Then install ``ptah_crowd`` into your virtualenv::

  $ cd ptah_crowd
  $ /path/to/virtualenv/bin/python setup.py develop

Now all that is remaining is telling the application to use
``ptah_crowd``.  This is really easy.  Two ways.

#1 - Edit the .ini File::

  $ cd examples/ptah_models
  $ edit settings.ini

Add `ptah_crowd` to the end of the `pyramid.includes` line::

  pyramid.includes = ptah pyramid_debugtoolbar ptah_crowd

#2 - Add it to the WSGI app::

  $ cd examples/ptah_models/ptah_models
  $ edit app.py
  
Below the ``config.include('ptah')`` statment you can add::

  config.include('ptah_crowd')

Then start pyramid::

  $ /path/to/virtualenv/bin/pserve settings.ini

To learn more about extending Pyramid you can read more in the documentation.
http://readthedocs.org/docs/pyramid/en/latest/narr/extending.html
