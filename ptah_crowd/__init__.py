# ptah_crowd package

from ptah_crowd.provider import CrowdUser
from ptah_crowd.provider import CrowdApplication
from ptah_crowd.provider import CrowdFactory
from ptah_crowd.provider import CROWD_APP_ID

from ptah_crowd.settings import CFG_ID_CROWD
from ptah_crowd.memberprops import get_properties
from ptah_crowd.memberprops import query_properties
from ptah_crowd.validation import initiate_email_validation

from ptah_crowd.schemas import UserSchema
from ptah_crowd.schemas import checkLoginValidator


# ptah_crowd include
def includeme(config):
    config.add_route(
        'ptah-principal-validate', '/validateaccount.html')

    # login routes
    config.add_route(
        'ptah-login', '/login.html', use_global_views=True)
    config.add_route(
        'ptah-logout', '/logout.html', use_global_views=True)
    config.add_route(
        'ptah-login-success', '/login-success.html', use_global_views=True)
    config.add_route(
        'ptah-login-suspended', '/login-suspended.html', use_global_views=True)

    # reset password
    config.add_route(
        'ptah-resetpassword', '/resetpassword.html')
    config.add_route(
        'ptah-resetpassword-form', '/resetpassword.html/*subpath')

    # registration
    config.add_route(
        'ptah-join', '/join.html', use_global_views=True)

    # for management module
    config.add_route(
        CROWD_APP_ID, '# {0}'.format(CROWD_APP_ID), use_global_views=True)

    # scan
    config.scan('ptah_crowd')
