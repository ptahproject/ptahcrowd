import ptah
from pyramid.compat import text_
from pyramid.testing import DummyRequest
from pyramid.view import render_view_to_response
from pyramid.httpexceptions import HTTPForbidden


class TestForbiddenView(ptah.PtahTestCase):

    def test_forbidden(self):
        from ptah_crowd.forbidden import Forbidden

        class Context(object):
            """ """

        request = DummyRequest()
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
        from ptah_crowd.forbidden import Forbidden
        from pyramid.interfaces import IRootFactory

        class Root(object):
            """ """
            def __init__(self, request):
                self.request = request

        request = DummyRequest()
        request.url = 'http://example.com'
        request.application_url = 'http://example.com'

        self.registry.registerUtility(Root, IRootFactory)

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        self.assertIs(excview.__parent__, request.root)
        self.assertIsInstance(request.root, Root)

    def test_forbidden_user(self):
        from ptah_crowd.forbidden import Forbidden

        class Context(object):
            """ """
            __name__ = 'test'

        request = DummyRequest()
        request.root = Context()
        ptah.auth_service.set_userid('user')

        res = render_view_to_response(HTTPForbidden(), request)
        self.assertEqual(text_(res.status), '403 Forbidden')
        self.assertIn('<h1>Your are not allowed to access this part of site.</h1>',
                      res.text)

    def test_forbidden_custom_login(self):
        import ptah_crowd
        from ptah_crowd.forbidden import Forbidden

        class Context(object):
            """ """

        request = DummyRequest()
        request.url = 'http://example.com'
        request.root = Context()

        CFG = ptah.get_settings(ptah_crowd.CFG_ID_CROWD, self.registry)
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
        import ptah_crowd
        from ptah_crowd.forbidden import Forbidden

        class Context(object):
            """ """

        request = DummyRequest()
        request.url = 'http://example.com'
        request.root = Context()

        CFG = ptah.get_settings(ptah_crowd.CFG_ID_CROWD, self.registry)
        CFG['login-url'] = 'http://login.example.com'

        excview = Forbidden(HTTPForbidden(), request)
        excview.update()

        res = request.response

        self.assertIs(excview.__parent__, request.root)
        self.assertEqual(res.status, '302 Found')
        self.assertEqual(
            text_(res.headers['location']),
            'http://login.example.com?came_from=http%3A%2F%2Fexample.com')
