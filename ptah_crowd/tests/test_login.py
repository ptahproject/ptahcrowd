import transaction
import ptah
from ptah import config
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPException, HTTPFound

import ptah_crowd


class TestSuspended(PtahTestCase):

    def test_suspended_anon(self):
        from ptah_crowd import login

        request = DummyRequest()
        view = login.LoginSuspended(None, request)
        res = view.update()
        self.assertIsInstance(res, HTTPFound)

    def test_suspended_not(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login',
                         email='email', password='{plain}12345')
        CrowdFactory().add(user)

        uri = user.__uri__
        props = ptah_crowd.get_properties(uri)
        props.suspended = False

        request = DummyRequest()
        ptah.auth_service.set_userid(uri)

        request = DummyRequest()
        res = self.render_route_view(None, request, 'ptah-login-suspended')
        self.assertIsInstance(res, HTTPFound)

    def test_suspended(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login',
                         email='email', password='{plain}12345')
        CrowdFactory().add(user)

        uri = user.__uri__

        props = ptah_crowd.get_properties(uri)
        props.suspended = True

        ptah.auth_service.set_userid(user.__uri__)

        request = DummyRequest()
        res = self.render_route_view(None, request, 'ptah-login-suspended')

        self.assertIn('Your account is suspended', res.text)


class TestLogout(PtahTestCase):

    def test_logout_anon(self):
        from ptah_crowd import login

        request = DummyRequest()
        res = login.logout(request)
        self.assertIsInstance(res, HTTPFound)

    def test_logout(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login',
                         email='email', password='{plain}12345')
        CrowdFactory().add(user)

        uri = user.__uri__

        request = DummyRequest()
        request.environ['HTTP_HOST'] = 'example.com'
        ptah.auth_service.set_userid(uri)

        res = login.logout(request)
        self.assertIsInstance(res, HTTPFound)
        self.assertIsNone(ptah.auth_service.get_userid())


class TestLogoutSuccess(PtahTestCase):

    def test_login_success_anon(self):
        from ptah_crowd import login

        request = DummyRequest()
        request.environ['HTTP_HOST'] = 'example.com'

        res = self.render_route_view(None, request, 'ptah-login-success')

        self.assertEqual(
            res.headers['location'], 'http://example.com/login.html')

    def test_login_success(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login',
                         email='email', password='{plain}12345')
        CrowdFactory().add(user)

        uri = user.__uri__

        request = DummyRequest()
        ptah.auth_service.set_userid(uri)

        res = self.render_route_view(None, request, 'ptah-login-success')
        self.assertIn('You are now logged in', res.text)


class TestLogin(PtahTestCase):

    def test_login_auth(self):
        from ptah_crowd import login

        request = DummyRequest()

        ptah.auth_service.set_userid('test')

        res = login.LoginForm(None, request)()

        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.headers['location'],
                         'http://example.com/login-success.html')

    def test_login_update(self):
        from ptah_crowd import login

        request = DummyRequest()

        cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD)
        cfg['join'] = False
        cfg['joinurl'] = 'http://test/login.html'

        form = login.LoginForm(None, request)
        form.update()
        self.assertFalse(form.join)
        self.assertEqual(form.joinurl, 'http://test/login.html')

        res = login.LoginForm(None, request)()
        self.assertNotIn('head over to the registration form', res.text)

    def test_login_update_join(self):
        from ptah_crowd import login

        request = DummyRequest()
        request.registry = self.registry

        cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD, self.registry)
        cfg['join'] = True
        cfg['joinurl'] = ''

        form = login.LoginForm(None, request)
        form.update()
        self.assertTrue(form.join)
        self.assertEqual(form.joinurl, 'http://example.com/join.html')

        #self.assertIn('head over to the registration form', res.text)

    def test_login(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login',
                         email='email', password='{plain}12345')
        CrowdFactory().add(user)

        uri = user.__uri__

        request = DummyRequest()

        form = login.LoginForm(None, request)
        form.update()
        data, errors = form.extract()
        self.assertEqual(len(errors), 2)

        form.handleLogin()
        self.assertIn('Please fix indicated errors.',
                      ptah.render_messages(request))

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = login.LoginForm(None, request)
        form.update()
        res = form.handleLogin()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'],
                         'http://example.com/login-success.html')

    def test_login_came_from(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login',
                         email='email', password='{plain}12345')
        CrowdFactory().add(user)

        uri = user.__uri__

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'},
            GET={'came_from': 'http://example.com/ptah-manage/'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = login.LoginForm(None, request)
        form.update()
        res = form.handleLogin()

        self.assertEqual(res.headers['location'],
                         'http://example.com/ptah-manage/')

    def test_login_wrong_login(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login',
                         email='email', password='{plain}12345')
        CrowdFactory().add(user)

        uri = user.__uri__

        request = DummyRequest(
            POST={'login': 'login1', 'password': '123456'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = login.LoginForm(None, request)
        form.update()
        form.handleLogin()

        self.assertIn('You enter wrong login or password',
                      ptah.render_messages(request))

    def test_login_unvalidated(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login',
                         email='email', password='{plain}12345')
        CrowdFactory().add(user)

        uri = user.__uri__
        ptah_crowd.get_properties(uri).validated = False

        cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD)
        cfg['allow-unvalidated'] = False

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = login.LoginForm(None, request)
        form.update()
        form.handleLogin()

        self.assertIn('Account is not validated.',ptah.render_messages(request))

    def test_login_suspended(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login',
                         email='email', password='{plain}12345')
        CrowdFactory().add(user)

        uri = user.__uri__
        user.properties.suspended = True

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = login.LoginForm(None, request)
        form.update()
        res = form.handleLogin()

        self.assertEqual(res.headers['location'],
                         'http://example.com/login-suspended.html')
