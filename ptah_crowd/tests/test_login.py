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
        self.assertRaises(HTTPFound, view.update)

    def test_suspended_not(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.__uri__
        props = ptah_crowd.get_properties(uri)
        props.suspended = False
        transaction.commit()

        request = DummyRequest()
        ptah.authService.set_userid(uri)

        try:
            login.LoginSuspended.__view_renderer__(None, request, '')
        except Exception, res:
            pass
        self.assertIsInstance(res, HTTPFound)

    def test_suspended(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        uri = user.__uri__

        props = ptah_crowd.get_properties(uri)
        props.suspended = True

        ptah.authService.set_userid(user.__uri__)

        request = DummyRequest()
        res = login.LoginSuspended.__view_renderer__(None, request, '')

        self.assertIn('Your account is suspended', res)


class TestLogout(PtahTestCase):

    def test_logout_anon(self):
        from ptah_crowd import login

        request = DummyRequest()
        self.assertRaises(HTTPFound, login.logout, request)

    def test_logout(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.__uri__
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest()
        ptah.authService.set_userid(uri)

        try:
            login.logout(request)
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertIsNone(ptah.authService.get_userid())


class TestLogoutSuccess(PtahTestCase):

    def test_login_success_anon(self):
        from ptah_crowd import login

        request = DummyRequest()
        try:
            login.LoginSuccess.__view_renderer__(None, request, '')
        except HTTPFound, res:
            pass

        self.assertEqual(
            res.headers['location'], 'http://example.com/login.html')

    def test_login_success(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.__uri__
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest()
        ptah.authService.set_userid(uri)

        res = login.LoginSuccess.__view_renderer__(None, request, '')
        self.assertIn('You are now logged in', res)


class TestLogin(PtahTestCase):

    def test_login_auth(self):
        from ptah_crowd import login

        request = DummyRequest()

        ptah.authService.set_userid('test')
        try:
            login.LoginForm.__view_renderer__(None, request, None)
        except HTTPException, res:
            pass

        self.assertEqual(res.status, '302 Found')
        self.assertEqual(res.headers['location'],
                         'http://example.com/login-success.html')

    def test_login_update(self):
        from ptah_crowd import login

        request = DummyRequest()

        ptah_crowd.CONFIG['join'] = False
        ptah_crowd.CONFIG['joinurl'] = 'http://test/login.html'

        form = login.LoginForm(None, request)
        form.update()
        self.assertFalse(form.join)
        self.assertEqual(form.joinurl, 'http://test/login.html')

        res = login.LoginForm.__view_renderer__(None, request, '')
        self.assertNotIn('head over to the registration form', res)

    def test_login_update_join(self):
        from ptah_crowd import login

        request = DummyRequest()

        ptah_crowd.CONFIG['join'] = True
        ptah_crowd.CONFIG['joinurl'] = ''

        form = login.LoginForm(None, request)
        form.update()
        self.assertTrue(form.join)
        self.assertEqual(form.joinurl, 'http://example.com/join.html')

        res = login.LoginForm.__view_renderer__(None, request, '')
        self.assertIn('head over to the registration form', res)

    def test_login(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'login', 'email',
                         password = '{plain}12345')
        uri = user.__uri__
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest()

        form = login.LoginForm(None, request)
        form.update()
        data, errors = form.extract()
        self.assertEqual(len(errors), 2)

        form.handleLogin()
        self.assertIn('Please fix indicated errors.',
                      request.session['msgservice'][0])

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'})

        form = login.LoginForm(None, request)
        form.update()
        data, errors = form.extract()

        try:
            form.handleLogin()
        except Exception, res:
            pass

        self.assertEqual(res.headers['location'],
                         'http://example.com/login-success.html')

    def test_login_came_from(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'login', 'email',
                         password = '{plain}12345')
        uri = user.__uri__
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'},
            GET={'came_from': 'http://example.com/ptah-manage/'})

        form = login.LoginForm(None, request)
        form.update()
        data, errors = form.extract()

        try:
            form.handleLogin()
        except Exception, res:
            pass

        self.assertEqual(res.headers['location'],
                         'http://example.com/ptah-manage/')

    def test_login_wrong_login(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'login', 'email',
                         password = '{plain}12345')
        uri = user.__uri__
        Session.add(user)
        Session.flush()
        transaction.commit()

        request = DummyRequest(
            POST={'login': 'login1', 'password': '123456'})

        form = login.LoginForm(None, request)
        form.update()
        form.handleLogin()

        self.assertIn('You enter wrong login or password',
                      request.session['msgservice'][0])

    def test_login_unvalidated(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'login', 'email',
                         password = '{plain}12345')
        uri = user.__uri__
        Session.add(user)
        ptah_crowd.get_properties(uri).validated = False
        transaction.commit()

        ptah_crowd.CONFIG['allow-unvalidated'] = False

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'})

        form = login.LoginForm(None, request)
        form.update()
        form.handleLogin()

        self.assertIn('Account is not validated.',
                      request.session['msgservice'][0])

    def test_login_suspended(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, Session
        user = CrowdUser('name', 'login', 'email',
                         password = '{plain}12345')
        uri = user.__uri__
        Session.add(user)
        ptah_crowd.get_properties(uri).suspended = True
        transaction.commit()

        request = DummyRequest(
            POST={'login': 'login', 'password': '12345'})

        form = login.LoginForm(None, request)
        form.update()
        try:
            form.handleLogin()
        except Exception, res:
            pass

        self.assertEqual(res.headers['location'],
                         'http://example.com/login-suspended.html')
