import ptah
from ptah.testing import PtahTestCase
from pyramid.httpexceptions import HTTPFound, HTTPForbidden


class TestJoin(PtahTestCase):

    _includes = ('ptahcrowd',)

    def test_join_auth(self):
        from ptahcrowd.registration import Registration

        request = self.make_request()
        ptah.auth_service.set_userid('test')

        form = Registration(None, request)
        res = form()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(
            res.headers['location'], 'http://example.com')

    def test_join_disabled(self):
        import ptahcrowd
        from ptahcrowd.registration import Registration

        cfg = ptah.get_settings(ptahcrowd.CFG_ID_CROWD)
        cfg['join'] = False

        request = self.make_request()
        form = Registration(None, request)
        res = form()
        self.assertIsInstance(res, HTTPForbidden)

    def test_join_error(self):
        from ptahcrowd.provider import CrowdUser
        from ptahcrowd.registration import Registration

        user = CrowdUser(username='username', email='email')
        ptah.get_session().add(user)
        ptah.get_session().flush()

        request = self.make_request(
            POST = {'username': 'test',
                    'email': 'custom login',
                    'password': '12345',
                    'confirm_password': '123456'})

        form = Registration(None, request)
        form.update_form()

        data, errors = form.extract()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].msg[0], 'Invalid email address')

        form.register_handler()
        self.assertIn('Please fix indicated errors.',
                      request.render_messages())

        request = self.make_request(
            POST = {'username': 'test',
                    'email': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '12345'})
        form = Registration(None, request)
        form.update_form()
        data, errors = form.extract()
        self.assertEqual(len(errors), 0)

    def test_join(self):
        from ptahcrowd.provider import CrowdUser
        from ptahcrowd.registration import Registration

        user = CrowdUser(username='username', email='email')
        ptah.get_session().add(user)
        ptah.get_session().flush()

        class Stub(object):
            status = ''
            def send(self, frm, to, msg):
                Stub.status = 'Email has been sended'

        MAIL = ptah.get_settings(ptah.CFG_ID_PTAH)
        MAIL['mailer'] = Stub()

        request = self.make_request(
            POST = {'username': 'test',
                    'email': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '12345'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = Registration(None, request)
        form.update_form()
        res = form.register_handler()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'],
                         'http://example.com/login-success.html')

        user = ptah.auth_service.get_principal_bylogin('test@example.com')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.name, 'test')

    def test_join_unvalidated(self):
        import ptahcrowd
        from ptahcrowd.provider import CrowdUser
        from ptahcrowd.registration import Registration

        user = CrowdUser(username='username', email='email')
        ptah.get_session().add(user)
        ptah.get_session().flush()

        class Stub(object):
            status = ''
            def send(self, frm, to, msg):
                Stub.status = 'Email has been sended'

        MAIL = ptah.get_settings(ptah.CFG_ID_PTAH)
        MAIL['mailer'] = Stub()

        CROWD = ptah.get_settings(ptahcrowd.CFG_ID_CROWD)
        CROWD['allow-unvalidated'] = False

        request = self.make_request(
            POST = {'username': 'test',
                    'email': 'test@example.com',
                    'password': '12345',
                    'confirm_password': '12345'})
        form = Registration(None, request)
        form.update_form()
        res = form.register_handler()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'http://example.com')

        user = ptah.auth_service.get_principal_bylogin('test@example.com')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.username, 'test')

        self.assertIn('Validation email has been sent.',
                      request.render_messages())
