""" introspect module """
import ptah
import sqlalchemy as sqla
from zope import interface
from pyramid.httpexceptions import HTTPFound
from ptah import view, form, config, manage

from settings import _
from provider import CrowdUser
from memberprops import get_properties, MemberProperties


@manage.module('crowd')
class CrowdModule(manage.PtahModule):
    __doc__ = u'Default user management. Create, edit, and activate users.'

    title = 'User management'

    def __getitem__(self, key):
        if key:
            user = CrowdUser.get(key)
            if user is not None:
                return UserWrapper(user, self)

        raise KeyError(key)


class UserWrapper(object):

    def __init__(self, user, parent):
        self.user = user
        self.__name__ = str(user.pid)
        self.__parent__ = parent
