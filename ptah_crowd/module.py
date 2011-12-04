""" introspect module """
import sqlalchemy as sqla
from zope import interface
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import view, form, config, manage

from ptah_crowd.settings import _
from ptah_crowd.provider import CrowdUser
from ptah_crowd.memberprops import get_properties, MemberProperties


@manage.module('crowd')
class CrowdModule(manage.PtahModule):
    __doc__ = 'Default user management. Create, edit, and activate users.'

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
