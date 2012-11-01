# ptahcrowd package

from ptahcrowd.provider import get_user_type
from ptahcrowd.provider import CrowdUser
from ptahcrowd.provider import CrowdGroup
from ptahcrowd.provider import CROWD_APP_ID

from ptahcrowd.settings import CFG_ID_AUTH
from ptahcrowd.settings import CFG_ID_CROWD
from ptahcrowd.validation import initiate_email_validation

from ptahcrowd.schemas import UserSchema
from ptahcrowd.schemas import checkLoginValidator

POPULATE_CREATE_ADMIN = 'ptah-crowd-admin'


# ptahcrowd include
def includeme(config):
    config.include('ptah')

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

    # templates
    config.add_layer('ptah-crowd', path='ptahcrowd:templates')

    # layout
    config.add_layout(
        'crowd', renderer='ptah-crowd:layout.lt', parent="workspace")

    # static assets
    config.add_static_view('_ptahcrowd', 'ptahcrowd:static')

    # scan
    config.scan('ptahcrowd')

    config.add_translation_dirs('ptahcrowd:locale')
