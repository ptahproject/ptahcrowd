"""Github Authentication"""
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


class GithubAuthenticationComplete(AuthenticationComplete):
    """Github auth complete"""


def includeme(config):
    config.add_route("github_login", "/github/login")
    config.add_route("github_process", "/github/process",
                     use_global_views=True,
                     factory=github_process)
    config.add_view(github_login, route_name="github_login")


def github_login(request):
    """Initiate a github login"""
    cfg = ptah.get_settings(ptah_crowd.CFG_ID_AUTH, request.registry)

    scope = cfg['github_scope']
    client_id = cfg['github_id']

    gh_url = '{0}?{1}'.format(
        'https://github.com/login/oauth/authorize',
        url_encode({'scope': scope,
                    'client_id': client_id,
                    'redirect_uri': request.route_url('github_process')}))
    return HTTPFound(location=gh_url)


def github_process(request):
    """Process the github redirect"""
    code = request.GET.get('code')
    if not code:
        reason = request.GET.get('error', 'No reason provided.')
        return AuthenticationDenied(reason)

    cfg = ptah.get_settings(ptah_crowd.CFG_ID_AUTH, request.registry)

    client_id = cfg['github_id']
    client_secret = cfg['github_secret']

    # Now retrieve the access token with the code
    access_url ='{0}?{1}'.format(
        'https://github.com/login/oauth/access_token',
        url_encode({'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': request.route_url('github_process'),
                    'code': code}))

    r = requests.get(access_url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))

    try:
        access_token = parse_qs(r.content)['access_token'][0]
    except:
        return AuthenticationDenied("Can't get access_token.")

    entry = Storage.get_by_token(access_token)
    if entry is not None:
        return GithubAuthenticationComplete(entry)

    # Retrieve profile data
    graph_url = '{0}?{1}'.format('https://github.com/api/v2/json/user/show',
                                 url_encode({'access_token': access_token}))
    r = requests.get(graph_url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))

    print r.content
    data = loads(r.content)['user']

    profile = {}
    profile['id'] = data['id']
    profile['name'] = data['login']
    profile['displayName'] = data['name']
    profile['preferredUsername'] = data['login']
    profile['email'] = data.get('email', '')

    entry = Storage.create(access_token, 'github.com', profile)
    return GithubAuthenticationComplete(entry)
