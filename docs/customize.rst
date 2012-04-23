Customize crowd user
====================

There are two way of user customization. 

* Add additional information to user properties object:

  .. code-block:: python

    principal = ptah.auth_service.get_current_principal()

    props = ptah_crowd.get_properties(principal.__uri__)
    props.data['custom-data'] = 'DATA'


* Create new crowd user content type.


New user content
----------------

First of all CrowdUser is just :py:class:`ptahcms.Content` object.
So all you need if just create new content type and provide this information
to ptah crowd provider. There is one restriction:

* New user content class should inherit from :py:class:`ptah_crowd.CrowdUser` class.

Example:

.. code-block:: python

  import ptah
  import ptah_crowd

  class CustomUser(ptah_crowd.CrowdUser):

     __tablename__ = 'custom_users'

     __type__ = ptah.Type('custom-user')


To inform ``ptah_crowd`` about your content object you should set
``ptah_crowd.type`` settings. Modify you INI file add following 
line to you application definition section::

  ptah_crowd.type = "custom_users"




