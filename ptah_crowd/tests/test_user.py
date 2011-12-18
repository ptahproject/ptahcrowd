import transaction
import ptah
from ptah import config
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPException, HTTPFound, HTTPForbidden

import ptah_crowd


class TestCreateUser(PtahTestCase):

    def test_create_user_back(self):
        from ptah_crowd.module import CrowdModule
        from ptah_crowd.user import CreateUserForm

        request = DummyRequest(
            POST = {'form.buttons.back': 'Back'})
        mod = CrowdModule(None, request)

        view = CreateUserForm(mod, request)
        res = view.update()
        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')

    def test_create_user_error(self):
        from ptah_crowd.module import CrowdModule
        from ptah_crowd.user import CreateUserForm

        f = CreateUserForm(None, None)

        request = DummyRequest(
            POST = {'form.buttons.create': 'Create'})
        request.POST[CreateUserForm.csrfname] = \
            request.session.get_csrf_token()
        mod = CrowdModule(None, request)

        view = CreateUserForm(mod, request)
        view.update()
        self.assertIn(
            'Please fix indicated errors.',
            ptah.render_messages(request))

    def test_create_user(self):
        from ptah_crowd.module import CrowdModule
        from ptah_crowd.user import CreateUserForm

        f = CreateUserForm(None, None)

        request = DummyRequest(
            POST = {'name': 'NKim',
                    'login': 'ptah@ptahproject.org',
                    'password': '12345',
                    'validated': 'false',
                    'suspended': 'true',
                    'form.buttons.create': 'Create'})
        request.POST[CreateUserForm.csrfname] = \
            request.session.get_csrf_token()

        mod = CrowdModule(None, request)

        view = CreateUserForm(mod, request)
        res = view.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '.')
        self.assertIn(
            'User has been created.', ptah.render_messages(request))

        user = ptah.auth_service.get_principal_bylogin('ptah@ptahproject.org')
        self.assertEqual(user.name, 'NKim')
        self.assertEqual(user.login, 'ptah@ptahproject.org')

        props = ptah_crowd.query_properties(user.__uri__)
        self.assertTrue(props.suspended)
        self.assertFalse(props.validated)


class TestModifyUser(PtahTestCase):

    def _user(self):
        from ptah_crowd.provider import CrowdUser, CrowdFactory
        user = CrowdUser(title='name', login='ptah@local', email='ptah@local')
        CrowdFactory().add(user)
        return user

    def test_modify_user_back(self):
        from ptah_crowd.user import ModifyUserForm

        user = self._user()

        request = DummyRequest(
            POST = {'form.buttons.back': 'Back'})

        view = ModifyUserForm(user, request)
        res = view.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

    def test_modify_user_changepwd(self):
        from ptah_crowd.user import ModifyUserForm

        user = self._user()

        request = DummyRequest(
            POST = {'form.buttons.changepwd': 'Change'})

        view = ModifyUserForm(user, request)
        res = view.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], 'password.html')

    def test_modify_user_forbidden(self):
        from ptah_crowd.user import ModifyUserForm

        user = self._user()

        request = DummyRequest(
            POST = {'form.buttons.modify': 'Modify',
                    'name': 'NKim',
                    'login': 'ptah@ptahproject.org',
                    'password': '12345',
                    'validated': 'false',
                    'suspended': 'true',
                    })

        view = ModifyUserForm(user, request)
        res = None
        try:
            view.update()
        except Exception as err:
            res = err

        self.assertIsInstance(res, HTTPForbidden)
        self.assertEqual(str(res), 'Form authenticator is not found.')

    def test_modify_user_error(self):
        from ptah_crowd.user import ModifyUserForm

        user = self._user()

        request = DummyRequest(
            POST = {'form.buttons.modify': 'Modify'})

        view = ModifyUserForm(user, request)
        view.csrf = False
        view.update()

        self.assertIn(
            'Please fix indicated errors.',
            ptah.render_messages(request))

    def test_modify_user(self):
        from ptah_crowd.user import ModifyUserForm

        user = self._user()
        f = ModifyUserForm(None, None)

        request = DummyRequest(
            POST = {'form.buttons.modify': 'Modify',
                    'name': 'NKim',
                    'login': 'ptah@ptahproject.org',
                    'password': '12345',
                    'validated': 'false',
                    'suspended': 'true'})

        view = ModifyUserForm(user, request)
        view.csrf = False
        view.update()

        self.assertEqual(user.name, 'NKim')
        self.assertEqual(user.login, 'ptah@ptahproject.org')

    def test_modify_user_remove(self):
        from ptah_crowd.user import ModifyUserForm
        from ptah_crowd.provider import CrowdUser

        user = self._user()

        request = DummyRequest(
            POST = {'form.buttons.remove': 'Remove'})

        view = ModifyUserForm(user, request)
        view.csrf = False
        res = view.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

        user = ptah.resolve(user.__uri__)
        self.assertIsNone(user)


class TestChangePassword(PtahTestCase):

    def _user(self):
        from ptah_crowd.provider import CrowdUser, CrowdFactory
        user = CrowdUser(title='name', login='ptah@local', email='ptah@local')
        CrowdFactory().add(user)
        return user

    def test_change_password_user_back(self):
        from ptah_crowd.user import ChangePasswordForm

        user = self._user()

        request = DummyRequest(
            POST = {'form.buttons.back': 'Back'})

        view = ChangePasswordForm(user, request)
        res = view.update()

        self.assertIsInstance(res, HTTPFound)
        self.assertEqual(res.headers['location'], '..')

    def test_change_password_forbidden(self):
        from ptah_crowd.user import ChangePasswordForm

        user = self._user()

        request = DummyRequest(
            POST = {'form.buttons.change': 'Change',
                    'password': '12345',
                    })

        view = ChangePasswordForm(user, request)
        res = None
        try:
            view.update()
        except Exception as err:
            res = err

        self.assertIsInstance(res, HTTPForbidden)
        self.assertEqual(str(res), 'Form authenticator is not found.')

    def test_change_password_error(self):
        from ptah_crowd.user import ChangePasswordForm

        user = self._user()
        f = ChangePasswordForm(None, None)

        request = DummyRequest(
            POST = {'form.buttons.change': 'Change'})

        view = ChangePasswordForm(user, request)
        view.csrf = False
        view.update()

        self.assertIn(
            'Please fix indicated errors.', ptah.render_messages(request))

    def test_change_password(self):
        from ptah_crowd.user import ChangePasswordForm

        user = self._user()
        f = ChangePasswordForm(None, None)

        request = DummyRequest(
            POST = {'form.buttons.change': 'Change',
                    'password': '12345'})

        request.POST[ChangePasswordForm.csrfname] = \
                                             request.session.get_csrf_token()

        view = ChangePasswordForm(user, request)
        view.update()

        self.assertEqual(user.password, '{plain}12345')
