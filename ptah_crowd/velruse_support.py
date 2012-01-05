import json
import sqlalchemy as sqla
from sqlalchemy.sql import select, delete
from datetime import datetime, timedelta
from pyramid.view import view_config
from pyramid.config import Configurator
from pyramid.events import ApplicationCreated
from pyramid.threadlocal import get_current_registry

import ptah
import ptah_crowd


@ptah.subscriber(ApplicationCreated)
def settings_initialized(ev):
    registry = get_current_registry()

    cfg = ptah.get_settings(ptah_crowd.CFG_ID_AUTH, registry)
    providers = cfg['providers']
    if not providers:
        return

    config = Configurator(registry, autocommit=True)

    for provider in providers:
        print 'ptah_crowd.providers.{0}'.format(provider)
        config.include(
            'ptah_crowd.providers.{0}'.format(provider),
            route_prefix='/crowd-auth-provider')
    

@view_config(context='ptah_crowd.providers.AuthenticationComplete')
def auth_complete_view(context, request):
    endpoint = request.registry.settings.get('velruse.endpoint')
    #token = generate_token()
    #storage = request.registry.velruse_store
    if 'birthday' in context.profile:
        context.profile['birthday'] = \
                context.profile['birthday'].strfime('%Y-%m-%d')
    result_data = {
        'profile': context.profile,
        'credentials': context.credentials,
    }
    print result_data
    #storage.store(token, result_data, expires=300)
    #form = redirect_form(endpoint, token)
    #return Response(body=form)


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
