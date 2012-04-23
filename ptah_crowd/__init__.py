# ptah_crowd package

from ptah_crowd.provider import get_user_type
from ptah_crowd.provider import CrowdUser
from ptah_crowd.provider import CrowdApplication
from ptah_crowd.provider import CrowdFactory
from ptah_crowd.provider import CROWD_APP_ID

from ptah_crowd.settings import CFG_ID_AUTH
from ptah_crowd.settings import CFG_ID_CROWD
from ptah_crowd.memberprops import get_properties
from ptah_crowd.memberprops import query_properties
from ptah_crowd.validation import initiate_email_validation

from ptah_crowd.schemas import UserSchema
from ptah_crowd.schemas import checkLoginValidator

POPULATE_CREATE_ADMIN = 'ptah-crowd-admin'


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
        'ptah-resetpassword',
        '/resetpassword.html', use_global_views=True)
    config.add_route(
        'ptah-resetpassword-form',
        '/resetpassword.html/*subpath', use_global_views=True)

    # registration
    config.add_route(
        'ptah-join', '/join.html', use_global_views=True)

    # verify auth provider email
    config.add_route(
        'ptah-crowd-verify-email',
        '/auth-verify-email/*subpath',
        use_global_views=True)

    config.add_route(
        'ptah-crowd-verify-email-complete',
        '/auth-verify-email-complete/*subpath')

    # for management module
    config.add_route(
        CROWD_APP_ID, '# {0}'.format(CROWD_APP_ID), use_global_views=True)

    # static assets
    config.add_static_view('_ptah_crowd', 'ptah_crowd:static')

    # scan
    config.scan('ptah_crowd')

    config.add_translation_dirs('ptah_crowd:locale')
