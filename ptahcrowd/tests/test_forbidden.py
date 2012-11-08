import ptah
from pyramid.compat import text_
from pyramid.view import render_view_to_response
from pyramid.httpexceptions import HTTPForbidden


class TestForbiddenView(ptah.PtahTestCase):

    _includes = ('ptahcrowd',)

    def test_forbidden(self):
        from ptahcrowd.forbidden import Forbidden

        class Context(object):
            """ """

        request = self.make_request()
        request.url = 'http://example.com'
        request.application_url = 'http://example.com'
        request.root = Context()

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        res = request.response

        self.assertIs(excview.__parent__, request.root)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(
            text_(res.headers['location']),
            'http://example.com/login.html?came_from=http%3A%2F%2Fexample.com')

        excview = Forbidden(HTTPForbidden(), request)
        res = excview()
        self.assertEqual(res.status, '302 Found')

    def test_forbidden_default_root(self):
        from ptahcrowd.forbidden import Forbidden
        from pyramid.interfaces import IRootFactory

        class Root(object):
            """ """
            def __init__(self, request):
                self.request = request

        request = self.make_request()
        request.url = 'http://example.com'
        request.application_url = 'http://example.com'

        self.registry.registerUtility(Root, IRootFactory)

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        self.assertIs(excview.__parent__, request.root)
        self.assertIsInstance(request.root, Root)

    def test_forbidden_user(self):
        class Context(object):
            """ """
            __name__ = 'test'

        request = self.request
        request.root = Context()
        ptah.auth_service.set_userid('user')

        class Principal(object):
            pass

        def get_principal():
            return Principal()

        orig = ptah.auth_service.get_current_principal
        ptah.auth_service.get_current_principal = get_principal

        res = render_view_to_response(HTTPForbidden(), request)
        ptah.auth_service.get_current_principal = orig

        self.assertEqual(text_(res.status), '403 Forbidden')
        self.assertIn(
            '<h1>Your are not allowed to access this part of site.</h1>',
            res.text)

    def test_forbidden_custom_login(self):
        import ptahcrowd
        from ptahcrowd.forbidden import Forbidden

        class Context(object):
            """ """

        request = self.make_request()
        request.url = 'http://example.com'
        request.root = Context()

        CFG = ptah.get_settings(ptahcrowd.CFG_ID_CROWD, self.registry)
        CFG['login-url'] = '/custom-login.html'

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        res = request.response

        self.assertIs(excview.__parent__, request.root)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(
            text_(res.headers['location']),
            'http://example.com/custom-login.html?came_from=http%3A%2F%2Fexample.com')

    def test_forbidden_custom_login_domain(self):
        import ptahcrowd
        from ptahcrowd.forbidden import Forbidden

        class Context(object):
            """ """

        request = self.make_request()
        request.url = 'http://example.com'
        request.root = Context()

        CFG = ptah.get_settings(ptahcrowd.CFG_ID_CROWD, self.registry)
        CFG['login-url'] = 'http://login.example.com'

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        res = request.response

        self.assertIs(excview.__parent__, request.root)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(
            text_(res.headers['location']),
            'http://login.example.com?came_from=http%3A%2F%2Fexample.com')
