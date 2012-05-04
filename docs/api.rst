API
---

  .. automodule:: ptah_crowd

Users
~~~~~

  .. autoclass:: CrowdUser


Validation
~~~~~~~~~~

  .. autofunction:: initiate_email_validation


Application
~~~~~~~~~~~

  .. autoclass:: CrowdApplication
  
  .. py:data:: CrowdFactory

     This is application factory for :py:class:`CrowdApplication` application 
     class. For exampe to add new user programmatically:

     .. code-block:: python

       import ptah
       import ptah_crowd

       # create new user
       user = ptah_crowd.CrowdUser(
          title = 'Ptah admin',
	  login = 'admin',
	  email = 'admin@ptahproject.org',
	  password = ptah.pwd_tool.encode('12345'))

       # add user to crowd app
       ptah_crowd.CrowdFactory().add(user)

       transaction.commit()
  
