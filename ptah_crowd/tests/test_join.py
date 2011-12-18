import transaction
import ptah
from ptah import config
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

import ptah_crowd


class TestJoin(PtahTestCase):

    def test_join_auth(self):
        from ptah_crowd.registration import Registration

        request = DummyRequest()
        ptah.auth_service.set_userid('test')

        form = Registration(None, request)
        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(
            res.headers['location'], 'http://example.com')

    def test_join_disabled(self):
        from ptah_crowd.registration import Registration

        cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD)
        cfg['join'] = False

        request = DummyRequest()
        form = Registration(None, request)
        res = form.update()
        self.assertIsInstance(res, HTTPForbidden)

    def test_join_error(self):
        from ptah_crowd.registration import Registration
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        uri = user.__uri__

        request = DummyRequest(
            POST = {'name': 'Test user',
                    'login': 'custom login',
                    'password': '12345',
                    'confirm_password': '123456'})

        form = Registration(None, request)
        form.update()

        data, errors = form.extract()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg[0], 'Invalid email address')

        form.register_handler()
        self.assertIn('Please fix indicated errors.',
                      ptah.render_messages(request))

        request = DummyRequest(
            POST = {'name': 'Test user',
                    'login': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '12345'})
        form = Registration(None, request)
        form.update()
        data, errors = form.extract()
        self.assertEqual(len(errors), 0)

    def test_join(self):
        import ptah
        from ptah_crowd.registration import Registration
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        uri = user.__uri__

        class Stub(object):
            status = ''
            def send(self, frm, to, msg):
                Stub.status = 'Email has been sended'

        MAIL = ptah.get_settings(ptah.CFG_ID_PTAH)
        MAIL['Mailer'] = Stub()

        request = DummyRequest(
            POST = {'name': 'Test user',
                    'login': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '12345'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = Registration(None, request)
        form.update()
        res = form.register_handler()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'],
                         'http://example.com/login-success.html')

        user = ptah.auth_service.get_principal_bylogin('test@example.com')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.name, 'Test user')

    def test_join_unvalidated(self):
        from ptah_crowd.registration import Registration
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        uri = user.__uri__

        class Stub(object):
            status = ''
            def send(self, frm, to, msg):
                Stub.status = 'Email has been sended'

        MAIL = ptah.get_settings(ptah.CFG_ID_PTAH)
        MAIL['Mailer'] = Stub()

        CROWD = ptah.get_settings(ptah_crowd.CFG_ID_CROWD)
        CROWD['allow-unvalidated'] = False

        request = DummyRequest(
            POST = {'name': 'Test user',
                    'login': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '12345'})
        form = Registration(None, request)
        form.update()
        res = form.register_handler()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'http://example.com')

        user = ptah.auth_service.get_principal_bylogin('test@example.com')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.name, 'Test user')

        self.assertIn('Validation email has been sent.',
                      ptah.render_messages(request))
