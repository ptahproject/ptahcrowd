"""Windows Live Authentication

doc: http://msdn.microsoft.com/en-us/library/hh243647.aspx
app: https://manage.dev.live.com/Applications/Index
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


class LiveAuthenticationComplete(AuthenticationComplete):
    """Live Connect auth complete"""


def includeme(config):
    config.add_route("live_login", "/live/login")
    config.add_route("live_process", "/live/process",
                     use_global_views=True,
                     factory=live_process)
    config.add_view(live_login, route_name="live_login")


def live_login(request):
    """Initiate a Live login"""
    cfg = ptah.get_settings(ptahcrowd.CFG_ID_AUTH, request.registry)

    scope = 'wl.basic wl.emails wl.signin'
    client_id = cfg['live_id']

    live_url = 'https://oauth.live.com/authorize?{0}&redirect_uri={1}'.format(
        url_encode({'scope': scope,
                    'client_id': client_id,
                    'response_type': "code"}),
        request.route_url('live_process'))

    return HTTPFound(location=live_url)


def live_process(request):
    """Process the Live redirect"""
    if 'error' in request.GET:
        raise ThirdPartyFailure(request.GET.get('error_description',
                                'No reason provided.'))

    code = request.GET.get('code')
    if not code:
        reason = request.GET.get('error_reason', 'No reason provided.')
        return AuthenticationDenied(reason)

    cfg = ptah.get_settings(ptahcrowd.CFG_ID_AUTH, request.registry)

    client_id = cfg['live_id']
    client_secret = cfg['live_secret']

    # Now retrieve the access token with the code
    access_url = '{0}?{1}'.format(
        'https://oauth.live.com/token',
        url_encode({'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': request.route_url('live_process'),
                    'grant_type': 'authorization_code',
                    'code': code}))

    r = requests.get(access_url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))

    data = json.loads(r.content)
    access_token = data['access_token']

    entry = Storage.get_by_token(access_token)
    if entry is not None:
        return LiveAuthenticationComplete(entry)

    # Retrieve profile data
    url = '{0}?{1}'.format(
        'https://apis.live.net/v5.0/me',
        url_encode({'access_token': access_token}))
    r = requests.get(url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))

    profile = json.loads(r.content)

    id = profile['id']
    name = profile.get('name','')
    email = profile.get('emails',{}).get('preferred')
    verified = bool(email)

    entry = Storage.create(access_token, 'live',
                           uid = 'live:{0}'.format(id),
                           name = name,
                           email = email,
                           verified = verified,
                           profile = profile)

    return LiveAuthenticationComplete(entry)
