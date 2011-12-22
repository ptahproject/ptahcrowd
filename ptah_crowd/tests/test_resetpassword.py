import sys
import ptah
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden


class TestResetPassword(ptah.PtahTestCase):

    def setUp(self):
        super(TestResetPassword, self).setUp()

        self._app = self.config.make_wsgi_app()

    def test_resetpassword_cancel(self):
        from ptah_crowd.resetpassword import ResetPassword
        request = DummyRequest(
            POST={'form.buttons.cancel': 'Cancel'})

        form = ResetPassword(None, request)
        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'http://example.com')

    def test_resetpassword_required(self):
        from ptah_crowd.resetpassword import ResetPassword
        request = DummyRequest(
            POST={'form.buttons.reset': 'Reset'})

        form = ResetPassword(None, request)
        form.update()

        msg = ptah.render_messages(request)
        self.assertIn("System can't restore password for this user.", msg)

    def test_resetpassword(self):
        from ptah_crowd.resetpassword import ResetPassword
        from ptah_crowd.resetpassword import ResetPasswordTemplate
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        data = [1, None]
        def send(self):
            data[0] = 2
            data[1] = self.passcode

        ResetPasswordTemplate.send = send

        request = DummyRequest(
            POST={'login': 'login',
                  'form.buttons.reset': 'Reset'})

        form = ResetPassword(None, request)
        res = form.update()

        msg = ptah.render_messages(request)
        self.assertIn("Password reseting process has been initiated.", msg)

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'http://example.com')
        self.assertEqual(data[0], 2)

        principal = ptah.pwd_tool.get_principal(data[1])
        self.assertEqual(principal.name, 'name')
        self.assertEqual(principal.login, 'login')

        del ResetPasswordTemplate.send

    def test_resetpassword_form_unknown_passcode(self):
        from ptah_crowd.resetpassword import ResetPasswordForm

        request = DummyRequest(subpath=('unknown',))

        form = ResetPasswordForm(None, request)
        res = form.update()

        msg = ptah.render_messages(request)
        self.assertIn("Passcode is invalid.", msg)
        self.assertEqual(
            res.headers['location'], 'http://example.com/resetpassword.html')

    def test_resetpassword_form_update(self):
        from ptah_crowd.resetpassword import ResetPasswordForm
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        passcode = ptah.pwd_tool.generate_passcode(user)

        request = DummyRequest(subpath=(passcode,))

        form = ResetPasswordForm(None, request)
        form.update()

        self.assertEqual(form.title, user.name)
        self.assertEqual(form.passcode, passcode)

    def test_resetpassword_form_change_errors(self):
        from ptah_crowd.resetpassword import ResetPasswordForm
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        passcode = ptah.pwd_tool.generate_passcode(user)

        request = DummyRequest(
            subpath=(passcode,),
            POST = {'password': '12345', 'confirm_password': '123456',
                    'form.buttons.change': 'Change'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = ResetPasswordForm(None, request)
        form.update()

        msg = ptah.render_messages(request)
        self.assertIn("Please fix indicated errors.", msg)

    def test_resetpassword_form_change(self):
        from ptah_crowd.resetpassword import ResetPasswordForm
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        passcode = ptah.pwd_tool.generate_passcode(user)

        request = DummyRequest(
            subpath=(passcode,),
            POST = {'password': '123456', 'confirm_password': '123456',
                    'form.buttons.change': 'Change'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = ResetPasswordForm(None, request)
        res = form.update()

        msg = ptah.render_messages(request)
        self.assertIn("You have successfully changed your password.", msg)
        self.assertEqual(res.headers['location'], 'http://example.com')
        self.assertTrue(ptah.pwd_tool.check(user.password, '123456'))

    def test_resetpassword_template(self):
        from ptah_crowd.resetpassword import ResetPasswordTemplate
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        request = DummyRequest()
        passcode = ptah.pwd_tool.generate_passcode(user)

        template = ResetPasswordTemplate(user, request)
        template.passcode = passcode

        template.update()
        text = template.render()

        self.assertIn(
            "Password reseting process has been initiated. You must visit link below to complete password reseting:", text)

        self.assertIn(
            "http://example.com/resetpassword.html/%s/"%passcode, text)
