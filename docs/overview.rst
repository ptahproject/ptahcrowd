========
Overview
========

:py:mod:`ptah` does not require `ptah_crowd`.  The `ptah_simpleauth` package in
the examples repository demonstrates a fully working user/authentication
system.  If you want to understand how to build your own user/properties
subsystem - start at `ptah_simpleauth`.

This package contains a `out of the box` user application with the goal
of providing user-adjustable knobs.  These knobs should be sufficient for
many use-cases.  Writing web application user management is redundant work.
The goal of `ptah_crowd` is to satisfy 90% of the needs of developers.

`ptah_crowd` does not provide any authorization policies.

The `ptah_crowd` package provides a complete user system which includes:

  * user management
  
  * user registration
  
  * password reset
  
  * user properties
  
  * validation
  
  * de(activation)

  * user listing and views on users (for an application)**

In terms of `ptah` functionality it provides:

  * authentication checker
  
  * authentication provider
  
  * user & user properties models
  
  * ``Ptah Manage`` module to manage users

** denotes an optional feature.

installation
============

The easiest way to install ptah_crowd is::

  easy_install ptah_crowd

Or, if you're using `zc.buildout`, just specify ``ptah_crowd`` as a
required egg.

If you're developing a package or application that relies on ptah_crowd,
then add it as a dependency in your package's :file:`setup.py`, for example::

  from setuptools import setup, find_packages

  setup(
     # ...
    install_requires = [
        'ptah',
        'ptah_crowd',
       ])

.. note:: 

  This package requires Python 2.6 or newer.

  It also requires :mod:`ptah` 0.2 or above

schema
======

`ptah_crowd`

This table inherients from `ptah_content`.  This means the user
records has all of the attributes available from both `ptah_content` 
and `ptah_node`, nearly all of which are nullable.

+----------+---------+-------+---------+------------------------+
| Name     | Type    | Null  | Default | Comments               |
+==========+=========+=======+=========+========================+
| id       | int     | False | ''      | PK, FK ptah_content.id |
+----------+---------+-------+---------+------------------------+
| login    | varchar | True  | ''      | Maxlength 255          |
+----------+---------+-------+---------+------------------------+
| email    | varchar | True  | ''      | Maxlength 255          |
+----------+---------+-------+---------+------------------------+
| password | varchar | True  | ''      | Maxlength 255          |
+----------+---------+-------+---------+------------------------+

`ptah_crowd_memberprops`

The properties associated with a `ptah_crowd` user record.

+-----------+----------+-------+---------+------------------------+
| Name      | Type     | Null  | Default | Comments               |
+===========+==========+=======+=========+========================+
| uri       | varchar  | False |         | Primary Key            |
+-----------+----------+-------+---------+------------------------+
| joined    | datetime |       |         |                        |
+-----------+----------+-------+---------+------------------------+
| validated | boolean  | True  | False   |                        |
+-----------+----------+-------+---------+------------------------+
| suspended | boolean  | True  | False   |                        |
+-----------+----------+-------+---------+------------------------+
| data      | varchar  | True  | ''      | JSON                   |
+-----------+----------+-------+---------+------------------------+


