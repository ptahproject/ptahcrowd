import ptah
from pyramid.httpexceptions import HTTPFound


class TestResetPassword(ptah.PtahTestCase):

    _includes = ('ptahcrowd',)

    def setUp(self):
        super(TestResetPassword, self).setUp()

        self._app = self.config.make_wsgi_app()

    def test_resetpassword_cancel(self):
        from ptahcrowd.resetpassword import ResetPassword
        request = self.make_request(
            POST={'form.buttons.cancel': 'Cancel'})

        form = ResetPassword(None, request)
        res = form.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'http://example.com')

    def test_resetpassword_required(self):
        from ptahcrowd.resetpassword import ResetPassword
        request = self.make_request(
            POST={'form.buttons.reset': 'Reset'})

        form = ResetPassword(None, request)
        form.update()

        msg = request.render_messages()
        self.assertIn(
            "The system can't restore the password for this user.", msg)

    def test_resetpassword(self):
        from ptahcrowd.resetpassword import ResetPassword
        from ptahcrowd.resetpassword import ResetPasswordTemplate
        from ptahcrowd.provider import CrowdUser

        user = CrowdUser(name='name', login='login', email='email')
        CrowdUser.__type__.add(user)

        data = [1, None]
        def send(self):
            data[0] = 2
            data[1] = self.passcode

        ResetPasswordTemplate.send = send

        request = self.make_request(
            POST={'login': 'login',
                  'form.buttons.reset': 'Reset'})

        form = ResetPassword(None, request)
        res = form.update()

        msg = request.render_messages()
        self.assertIn("We have started resetting your password.", msg)

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'http://example.com')
        self.assertEqual(data[0], 2)

        principal = ptah.pwd_tool.get_principal(data[1])
        self.assertEqual(principal.name, 'name')
        self.assertEqual(principal.login, 'login')

        del ResetPasswordTemplate.send

    def test_resetpassword_form_unknown_passcode(self):
        from ptahcrowd.resetpassword import ResetPasswordForm

        request = self.make_request(subpath=('unknown',))

        form = ResetPasswordForm(None, request)
        res = form.update()

        msg = request.render_messages()
        self.assertIn("Passcode is invalid.", msg)
        self.assertEqual(
            res.headers['location'], 'http://example.com/resetpassword.html')

    def test_resetpassword_form_update(self):
        from ptahcrowd.provider import CrowdUser
        from ptahcrowd.resetpassword import ResetPasswordForm

        user = CrowdUser(name='name', login='login', email='email')
        CrowdUser.__type__.add(user)

        passcode = ptah.pwd_tool.generate_passcode(user)

        request = self.make_request(subpath=(passcode,))

        form = ResetPasswordForm(None, request)
        form.update()

        self.assertEqual(form.title, user.name)
        self.assertEqual(form.passcode, passcode)

    def test_resetpassword_form_change_errors(self):
        from ptahcrowd.provider import CrowdUser
        from ptahcrowd.resetpassword import ResetPasswordForm

        user = CrowdUser(name='name', login='login', email='email')
        CrowdUser.__type__.add(user)

        passcode = ptah.pwd_tool.generate_passcode(user)

        request = self.make_request(
            subpath=(passcode,),
            POST = {'password': '12345', 'confirm_password': '123456',
                    'form.buttons.change': 'Change'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = ResetPasswordForm(None, request)
        form.update()

        msg = request.render_messages()
        self.assertIn("Please fix indicated errors.", msg)

    def test_resetpassword_form_change(self):
        from ptahcrowd.provider import CrowdUser
        from ptahcrowd.resetpassword import ResetPasswordForm

        user = CrowdUser(name='name', login='login', email='email')
        CrowdUser.__type__.add(user)

        passcode = ptah.pwd_tool.generate_passcode(user)

        request = self.make_request(
            subpath=(passcode,),
            POST = {'password': '123456', 'confirm_password': '123456',
                    'form.buttons.change': 'Change'})
        request.environ['HTTP_HOST'] = 'example.com'

        form = ResetPasswordForm(None, request)
        res = form.update()

        msg = request.render_messages()
        self.assertIn("You have successfully changed your password.", msg)
        self.assertEqual(res.headers['location'], 'http://example.com')
        self.assertTrue(ptah.pwd_tool.check(user.password, '123456'))

    def test_resetpassword_template(self):
        from ptahcrowd.provider import CrowdUser
        from ptahcrowd.resetpassword import ResetPasswordTemplate

        user = CrowdUser(name='name', login='login', email='email')
        CrowdUser.__type__.add(user)

        request = self.make_request()
        passcode = ptah.pwd_tool.generate_passcode(user)

        template = ResetPasswordTemplate(user, request)
        template.passcode = passcode

        template.update()
        text = template.render()

        self.assertIn(
            "The password resetting process has been initiated. You must visit the link below to complete it:", text)

        self.assertIn(
            "http://example.com/resetpassword.html/%s/"%passcode, text)
