"""Windows Live Authentication

doc: http://msdn.microsoft.com/en-us/library/hh243647.aspx

"""
import datetime
import requests
from json import loads

from pyramid.compat import url_encode
from pyramid.httpexceptions import HTTPFound

import ptah
import ptah_crowd
from ptah_crowd.providers import AuthenticationComplete
from ptah_crowd.providers.exceptions import AuthenticationDenied
from ptah_crowd.providers.exceptions import ThirdPartyFailure


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
    cfg = ptah.get_settings(ptah_crowd.CFG_ID_AUTH, request.registry)

    scope = 'wl.basic wl.emails wl.signin'
    client_id = cfg['live_id']

    live_url = '{0}?{1}&redirect_uri={2}'.format(
        'https://oauth.live.com/authorize',
        url_encode({'scope': scope,
                    'client_id': client_id,
                    'redirect_uri': request.route_url('live_process'),
                    'response_type': "code"}))
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

    cfg = ptah.get_settings(ptah_crowd.CFG_ID_AUTH, request.registry)

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

    print r.content

    data = loads(r.content)
    access_token = data['access_token']

    # Retrieve profile data
    graph_url = '{0}?{1}'.format('https://apis.live.net/v5.0/me',
                                 url_encode(access_token=access_token))
    r = requests.get(graph_url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))
    live_profile = loads(r.content)
    profile = extract_live_data(live_profile)

    cred = {'oauthAccessToken': access_token}
    if 'refresh_token' in data:
        cred['oauthRefreshToken'] = data['refresh_token']
    return LiveAuthenticationComplete(profile=profile,
                                      credentials=cred)


def extract_live_data(data):
    """Extract and normalize Windows Live Connect data"""
    emails = data.get('emails', {})
    profile = {
        'accounts': [{'domain':'live.com', 'userid':data['id']}],
        'gender': data.get('gender'),
        'verifiedEmail': emails.get('preferred'),
        'updated': data.get('updated_time'),
        'name': {
            'formatted': data.get('name'),
            'familyName': data.get('last_name'),
            'givenName': data.get('first_name'),
        },
        'emails': [],
        'urls': [],
    }

    if emails.get('personal'):
        profile['emails'].append(
            {'type': 'personal', 'value': emails['personal']})
    if emails.get('business'):
        profile['emails'].append(
            {'type': 'business', 'value': emails['business']})
    if emails.get('preferred'):
        profile['emails'].append(
            {'type': 'preferred', 'value': emails['preferred'],
             'primary': True})
    if emails.get('account'):
        profile['emails'].append(
            {'type': 'account', 'value': emails['account']})
    if 'link' in data:
        profile['urls'].append(
            {'type': 'profile', 'value': data['link']})
    if 'birth_day' in data:
        try:
            profile['birthday'] = datetime.date(
                    int(data['birth_year']),
                    int(data['birth_month']),
                    int(data['birth_day']))
        except ValueError:
            pass
    return profile
