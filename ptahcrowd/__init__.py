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
        'ptahcrowd-login', '/login.html', use_global_views=True)
    config.add_route(
        'ptahcrowd-logout', '/logout.html', use_global_views=True)
    config.add_route(
        'ptahcrowd-login-success', '/login-success.html', use_global_views=True)
    config.add_route(
        'ptahcrowd-login-suspended', '/login-suspended.html', use_global_views=True)

    # reset password
    config.add_route(
        'ptahcrowd-resetpassword',
        '/resetpassword.html', use_global_views=True)
    config.add_route(
        'ptahcrowd-resetpassword-form',
        '/resetpassword.html/*subpath', use_global_views=True)

    # registration
    config.add_route(
        'ptahcrowd-join', '/join.html', use_global_views=True)

    # verify auth provider email
    config.add_route(
        'ptahcrowd-verify-email',
        '/auth-verify-email/*subpath',
        use_global_views=True)

    config.add_route(
        'ptahcrowd-verify-email-complete',
        '/auth-verify-email-complete/*subpath')

    # for management module
    config.add_route(
        CROWD_APP_ID, '# {0}'.format(CROWD_APP_ID), use_global_views=True)

    # templates
    config.add_layer('ptahcrowd', path='ptahcrowd:templates')

    # layout
    config.add_layout(
        'ptahcrowd', renderer='ptahcrowd:layout.lt', parent='ptah')

    # static assets
    config.add_static_view('_ptahcrowd', 'ptahcrowd:static')

    # scan
    config.scan('ptahcrowd')

    config.add_translation_dirs('ptahcrowd:locale')
