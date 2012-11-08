"""Google Authentication

Docs: http://code.google.com/apis/accounts/docs/OAuth2Login.html
OAuth App: https://code.google.com/apis/console   'Api Access'
"""
import json
import requests

from pyramid.compat import url_encode
from pyramid.httpexceptions import HTTPFound

import ptah
import ptahcrowd
from ptahcrowd.providers import Storage
from ptahcrowd.providers import AuthenticationComplete
from ptahcrowd.providers.exceptions import AuthenticationDenied
from ptahcrowd.providers.exceptions import ThirdPartyFailure


class GoogleAuthenticationComplete(AuthenticationComplete):
    """Google auth complete"""


def includeme(config):
    config.add_route("google_login", "/google/login")
    config.add_route("google_process", "/google/process",
                     use_global_views=True,
                     factory=google_process)
    config.add_view(google_login, route_name="google_login")


def google_login(request):
    """Initiate a google login"""
    cfg = ptah.get_settings(ptahcrowd.CFG_ID_AUTH, request.registry)

    client_id = cfg['google_id']

    go_url = '{0}?{1}&scope=https://www.googleapis.com/auth/userinfo.profile+https://www.googleapis.com/auth/userinfo.email'.format(
        'https://accounts.google.com/o/oauth2/auth',
        url_encode({'client_id': client_id,
                    'redirect_uri': request.route_url('google_process'),
                    'response_type': 'code'}))

    return HTTPFound(location=go_url)


def google_process(request):
    """Process the google redirect"""
    code = request.GET.get('code')
    if not code:
        reason = request.GET.get('error', 'No reason provided.')
        return AuthenticationDenied(reason)

    cfg = ptah.get_settings(ptahcrowd.CFG_ID_AUTH, request.registry)

    client_id = cfg['google_id']
    client_secret = cfg['google_secret']

    # Now retrieve the access token with the code
    r = requests.post('https://accounts.google.com/o/oauth2/token',
                      {'client_id': client_id,
                       'client_secret': client_secret,
                       'redirect_uri': request.route_url('google_process'),
                       'grant_type': 'authorization_code',
                       'code': code})
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))

    try:
        access_token = json.loads(r.content)['access_token']
    except:
        return AuthenticationDenied("Can't get access_token.")

    entry = Storage.get_by_token(access_token)
    if entry is not None:
        return GoogleAuthenticationComplete(entry)

    # Retrieve profile data
    graph_url = '{0}?{1}'.format(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        url_encode({'access_token': access_token}))
    r = requests.get(graph_url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))

    data = json.loads(r.content)

    id = data['id']
    name = data['name']
    email = data.get('email', '')

    entry = Storage.create(access_token, 'google',
                           uid = '{0}:{1}'.format('google', id),
                           name = name,
                           email = email,
                           verified = True,
                           profile = data)

    return GoogleAuthenticationComplete(entry)
