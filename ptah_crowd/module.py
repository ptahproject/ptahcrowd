""" crowd module """
from pyramid.interfaces import IRequest, IRouteRequest

import ptah
import ptah_crowd


@ptah.manage.module('crowd')
class CrowdModule(ptah.manage.PtahModule):
    __doc__ = 'Default user management. Create, edit, and activate users.'

    title = 'User management'

    def __getitem__(self, key):
        crowd = ptah_crowd.CrowdFactory()
        user = crowd.get(key)
        if user is not None:
            user.__parent__ = self
            user.__resource_url__ = None

            request = self.request
            request.request_iface = request.registry.getUtility(
                IRouteRequest, name=ptah_crowd.CROWD_APP_ID)

            return user

        raise KeyError(key)


ptah.uiaction(
    CrowdModule, **{'id': 'users',
                    'title': 'Users',
                    'action': '',
                    'sort_weight': 0.5,
                    'category': ptah.manage.MANAGE_ACTIONS})

ptah.uiaction(
    CrowdModule, **{'id': 'groups',
                    'title': 'Groups',
                    'action': 'groups.html',
                    'sort_weight': 0.6,
                    'category': ptah.manage.MANAGE_ACTIONS})
