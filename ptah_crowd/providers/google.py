"""Github Authentication

Docs: http://code.google.com/apis/accounts/docs/OAuth2Login.html
oAuth App: https://code.google.com/apis/console   'Api Access'
"""
from json import loads
from urlparse import parse_qs

import requests

from pyramid.compat import url_encode
from pyramid.httpexceptions import HTTPFound

import ptah
import ptah_crowd
from ptah_crowd.providers import Storage
from ptah_crowd.providers import AuthenticationComplete
from ptah_crowd.providers.exceptions import AuthenticationDenied
from ptah_crowd.providers.exceptions import ThirdPartyFailure


class GoogleAuthenticationComplete(AuthenticationComplete):
    """Google auth complete"""


def includeme(config):
    config.add_route("google_login", "/google/login")
    config.add_route("google_process", "/google/process",
                     use_global_views=True,
                     factory=google_process)
    config.add_view(google_login, route_name="google_login")


#https://accounts.google.com/o/oauth2/auth

#scope=
#https://www.googleapis.com/auth/userinfo.email
#https://www.googleapis.com/auth/userinfo.profile

#response_type=code
#redirect_uri=https://oauth2-login-demo.appspot.com/code
#approval_prompt=force
#state=/profile
#client_id=812741506391.apps.googleusercontent.com


def google_login(request):
    """Initiate a google login"""
    cfg = ptah.get_settings(ptah_crowd.CFG_ID_AUTH, request.registry)

    client_id = cfg['google_id']

    scope = 'https://www.googleapis.com/auth/userinfo.profile+https://www.googleapis.com/auth/userinfo.email'

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

    cfg = ptah.get_settings(ptah_crowd.CFG_ID_AUTH, request.registry)

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
        access_token = loads(r.content)['access_token']
    except:
        return AuthenticationDenied("Can't get access_token.")

    entry = Storage.get_by_token(access_token, 'google.com')
    if entry is not None:
        return GoogleAuthenticationComplete(entry)

    # Retrieve profile data
    graph_url = '{0}?{1}'.format(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        url_encode({'access_token': access_token}))
    r = requests.get(graph_url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))

    data = loads(r.content)

    profile = {}
    profile['id'] = data['id']
    profile['name'] = data['name']
    profile['displayName'] = data['name']
    profile['preferredUsername'] = data['name']
    profile['email'] = data.get('email', '')

    entry = Storage.create(access_token, 'google.com', profile)
    return GoogleAuthenticationComplete(entry)
