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
