import json
import logging
import sqlalchemy as sqla
from datetime import datetime, timedelta
from pyramid import security
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.events import ApplicationCreated
from pyramid.threadlocal import get_current_registry
from pyramid.httpexceptions import HTTPFound

import ptah
import ptah_crowd

log = logging.getLogger('ptah_crowd')


@ptah.subscriber(ApplicationCreated)
def settings_initialized(ev):
    registry = get_current_registry()

    cfg = ptah.get_settings(ptah_crowd.CFG_ID_AUTH, registry)
    providers = cfg['providers']
    if not providers:
        return

    config = Configurator(registry, autocommit=True)

    for provider in providers:
        log.info('Loaging "{0}" auth provider'.format(provider))
        config.include(
            'ptah_crowd.providers.{0}'.format(provider),
            route_prefix='/crowd-auth-provider')


@view_config(context='ptah_crowd.providers.AuthenticationComplete')
def auth_complete_view(context, request):
    principal = ptah.resolve(context.uri)

    info = ptah.auth_service.authenticate_principal(principal)

    if info.status:
        request.registry.notify(
            ptah.events.LoggedInEvent(principal))

        location = '%s/login-success.html'%request.application_url

        headers = security.remember(request, principal.__uri__)
        return HTTPFound(headers = headers, location = location)

    if info.arguments.get('suspended'):
        return HTTPFound(
            location='%s/login-suspended.html'%request.application_url)

    ptah.add_message(request, info.message, 'warning')
    return HTTPFound(location = '%s/login.html'%request.application_url)


#@view_config(context='velruse.exceptions.AuthenticationDenied')
def auth_denied_view(context, request):
    endpoint = request.registry.settings.get('velruse.endpoint')
    token = generate_token()
    storage = request.registry.velruse_store
    error_dict = {
        'code': context.code,
        'description': context.description,
    }
    storage.store(token, error_dict, expires=300)
    form = redirect_form(endpoint, token)
    return Response(body=form)


class AuthenticationComplete(object):
    """An AuthenticationComplete context object"""

    def __init__(self, entry):
        """Create an AuthenticationComplete object with user data"""
        self.uri = entry.uri
        self.profile = json.loads(entry.profile)


class Storage(ptah.get_base()):

    __tablename__ = 'ptah_crowd_auth_storage'

    uid = sqla.Column(
        sqla.String(255), primary_key=True, nullable=False)
    access_token = sqla.Column(
        sqla.String(255), nullable=False, index=True)
    uri = sqla.Column(sqla.String(255), nullable=False)
    profile = sqla.Column(sqla.Text(), nullable=False)
    expires = sqla.Column(sqla.DateTime())

    @classmethod
    def get_by_token(cls, access_token):
        return ptah.get_session().query(cls).filter(
            sqla.and_(cls.access_token == access_token)).first()

    @classmethod
    def create(cls, access_token, domain, profile, expires=None):
        session = ptah.get_session()
        tinfo = ptah_crowd.get_user_type()

        # create user
        user = tinfo.create(
            title=profile['displayName'],
            login='{0}:{1}'.format(domain, profile['name']),
            email=profile.get('email',''))

        schema = ptah.extract_uri_schema(user.__uri__)
        uri = '{0}:{1}-{2}'.format(schema, domain, profile['id'])

        existing_user = ptah.resolve(uri)
        if existing_user is not None:
            user = existing_user
            user.access_token = access_token
            user.domain = domain
            user.profile = json.dumps(profile)
            user.password = access_token
            user.email = profile['email']

            session.query(cls).filter(cls.uri == uri).delete()
        else:
            user.__uri__ = uri
            user.password = access_token
            print profile
            ptah_crowd.CrowdFactory().add(user)

        user.properties.validated = True

        # entry
        profile = json.dumps(profile)

        entry = cls(uri=user.__uri__,
                    access_token=access_token,
                    domain=domain,
                    profile=profile)

        session.add(entry)
        return entry

    @classmethod
    def delete(cls, key):
        ptah.get_session().query(cls).filter(cls.key == key).delete()
        return True

    @classmethod
    def purge_expired(cls):
        ptah.get_session().query(cls)\
            .filter(cls.expires < datetime.utcnow()).delete()
        return True
