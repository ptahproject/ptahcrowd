""" forbidden view """
import ptah.renderer
from pyramid.compat import url_encode
from pyramid import security
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.interfaces import IRootFactory
from pyramid.traversal import DefaultRootFactory
from pyramid.httpexceptions import HTTPFound, HTTPForbidden
from pyramid.view import view_config, render_view_to_response

import ptah
import ptahcrowd
from ptahcrowd.settings import _


@view_config(
    context=HTTPForbidden,
    renderer=ptah.renderer.layout('ptahcrowd:templates/forbidden.pt', 'ptahcrowd'))
class Forbidden(ptah.View):

    def update(self):
        request = self.request

        context = getattr(request, 'context', None)
        if context is None:
            context = getattr(request, 'root', None)

        if context is None:
            root_factory = request.registry.queryUtility(
                IRootFactory, default=DefaultRootFactory)
            context = root_factory(request)
            request.root = context

        self.__parent__ = context

        CFG = ptah.get_settings(ptahcrowd.CFG_ID_CROWD, self.request.registry)

        user = ptah.auth_service.get_userid()
        if user is not None:
            user = ptah.auth_service.get_current_principal()
            if user is None:
                request.response.headers = security.forget(request)

        if user is None:
            loginurl = CFG['login-url']
            if loginurl and not loginurl.startswith(('http://', 'https://')):
                loginurl = self.application_url + loginurl
            elif not loginurl:
                loginurl = self.application_url + '/login.html'

            location = '%s?%s'%(
                loginurl, url_encode({'came_from': request.url}))

            request.add_message(_('To access this part of the site, you need to log in with your credentials.'), 'info')

            response = request.response
            response.status = HTTPFound.code
            response.headers['location'] = location
            return response

        PTAH = ptah.get_settings(ptah.CFG_ID_PTAH, self.request.registry)
        self.email_address = PTAH['email_from_address']

        self.request.response.status = HTTPForbidden.code

    def __call__(self):
        result = self.update()
        if result is None:
            result = {}

        return result
