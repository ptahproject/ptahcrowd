""" forbidden view """
from pyramid.compat import text_type, url_encode
from pyramid.view import view_config
from pyramid.view import render_view_to_response
from pyramid.response import Response
from pyramid.renderers import render
from pyramid.interfaces import IRootFactory
from pyramid.traversal import DefaultRootFactory
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

import ptah
import ptah_crowd


@view_config(context=HTTPForbidden)
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

        CFG = ptah.get_settings(ptah_crowd.CFG_ID_CROWD, self.request.registry)

        user = ptah.auth_service.get_userid()
        if user is None:
            loginurl = CFG['login-url']
            if loginurl and not loginurl.startswith(('http://', 'https://')):
                loginurl = self.application_url + loginurl
            elif not loginurl:
                loginurl = self.application_url + '/login.html'

            location = '%s?%s'%(
                loginurl, url_encode({'came_from': request.url}))
            if isinstance(location, text_type):
                location = location.encode('utf-8')

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

        if isinstance(result, Response):
            return result

        request = self.request

        result['view'] = self
        result['request'] = request
        request.wrapped_response = result
        request.wrapped_body = render(
            'ptah_crowd:templates/forbidden.pt', result, request)

        name = ptah.wrap_layout('ptah-page')
        return render_view_to_response(self.__parent__, request, name)
