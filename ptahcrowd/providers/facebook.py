"""Facebook Authentication Views"""
import json
import uuid
import requests

from pyramid.compat import url_encode, urlparse
from pyramid.httpexceptions import HTTPFound

import ptah
import ptahcrowd
from ptahcrowd.providers import Storage, AuthenticationComplete
from ptahcrowd.providers.exceptions import AuthenticationDenied
from ptahcrowd.providers.exceptions import CSRFError
from ptahcrowd.providers.exceptions import ThirdPartyFailure


class FacebookAuthenticationComplete(AuthenticationComplete):
    """Facebook auth complete"""


def includeme(config):
    config.add_route("facebook_login", "/facebook/login")
    config.add_route("facebook_process", "/facebook/process",
                     use_global_views=True,
                     factory=facebook_process)
    config.add_view(facebook_login, route_name="facebook_login")


def facebook_login(request):
    """Initiate a facebook login"""
    cfg = ptah.get_settings(ptahcrowd.CFG_ID_AUTH, request.registry)

    scope = cfg['facebook_scope']
    if scope and 'email' not in scope:
        scope = '%s,email'%scope
    elif not scope:
        scope = 'email'

    client_id = cfg['facebook_id']

    request.session['facebook_state'] = state = uuid.uuid4().hex
    fb_url = '{0}?{1}'.format(
        'https://www.facebook.com/dialog/oauth/',
        url_encode({'scope': scope,
                    'client_id': client_id,
                    'redirect_uri': request.route_url('facebook_process'),
                    'state': state}))
    return HTTPFound(location=fb_url)


def facebook_process(request):
    """Process the facebook redirect"""
    if request.GET.get('state') != request.session.get('facebook_state'):
        raise CSRFError("CSRF Validation check failed. Request state %s is "
                        "not the same as session state %s" % (
                        request.GET.get('state'), request.session.get('state')
                        ))
    del request.session['facebook_state']

    code = request.GET.get('code')
    if not code:
        reason = request.GET.get('error_reason', 'No reason provided.')
        return AuthenticationDenied(reason)

    cfg = ptah.get_settings(ptahcrowd.CFG_ID_AUTH, request.registry)

    client_id = cfg['facebook_id']
    client_secret = cfg['facebook_secret']

    # Now retrieve the access token with the code
    access_url = '{0}?{1}'.format(
        'https://graph.facebook.com/oauth/access_token',
        url_encode({'client_id': client_id,
                    'client_secret': client_secret,
                    'redirect_uri': request.route_url('facebook_process'),
                    'code': code}))
    r = requests.get(access_url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))

    access_token = urlparse.parse_qs(r.content)['access_token'][0]

    entry = Storage.get_by_token(access_token)
    if entry is not None:
        return FacebookAuthenticationComplete(entry)

    # Retrieve profile data
    graph_url = '{0}?{1}'.format('https://graph.facebook.com/me',
                                 url_encode({'access_token': access_token}))
    r = requests.get(graph_url)
    if r.status_code != 200:
        raise ThirdPartyFailure("Status %s: %s" % (r.status_code, r.content))

    profile = json.loads(r.content)

    id = profile['id']
    name = profile['name']
    email = profile.get('email','')
    verified = profile.get('verified', False)

    entry = Storage.create(access_token, 'facebook',
                           uid = '{0}:{1}'.format('facebook', id),
                           name = name,
                           email = email,
                           verified = verified,
                           profile = profile)
    return FacebookAuthenticationComplete(entry)
