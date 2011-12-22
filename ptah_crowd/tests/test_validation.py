import os
from pyramid.testing import DummyRequest
from pyramid.compat import text_
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah.authentication import AuthInfo

import ptah_crowd


class Principal(object):

    def __init__(self, uri, name, login):
        self.__uri__ = uri
        self.name = name
        self.login = login


class TestValidation(ptah.PtahTestCase):

    def test_validation_auth_checker_validation(self):
        from ptah_crowd.validation import validationAndSuspendedChecker

        principal = Principal('1', 'user', 'user')

        props = ptah_crowd.get_properties(principal.__uri__)
        props.validated = False

        cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD)

        # validation disabled
        info = AuthInfo(principal, True)
        cfg['validation'] = False
        self.assertTrue(validationAndSuspendedChecker(info))

        info = AuthInfo(principal, True)
        cfg['allow-unvalidated'] = False
        self.assertTrue(validationAndSuspendedChecker(info))

        # validation enabled
        info = AuthInfo(principal, True)
        cfg['validation'] = True
        cfg['allow-unvalidated'] = False
        self.assertFalse(validationAndSuspendedChecker(info))
        self.assertEqual(info.message, 'Account is not validated.')

        info = AuthInfo(principal, True)
        cfg['allow-unvalidated'] = True
        self.assertTrue(validationAndSuspendedChecker(info))

        # validated
        props = ptah_crowd.get_properties(principal.__uri__)
        props.validated = True

        info = AuthInfo(principal, True)
        cfg['validation'] = True
        self.assertTrue(validationAndSuspendedChecker(info))

    def test_validation_auth_checker_suspended(self):
        from ptah.authentication import AuthInfo
        from ptah_crowd.validation import validationAndSuspendedChecker

        principal = Principal('2', 'user', 'user')

        props = ptah_crowd.get_properties(principal.__uri__)
        props.validated = True
        props.suspended = False

        info = AuthInfo(principal, True)
        self.assertTrue(validationAndSuspendedChecker(info))

        props.suspended = True

        info = AuthInfo(principal, True)
        self.assertFalse(validationAndSuspendedChecker(info))
        self.assertEqual(info.message, 'Account is suspended.')

    def test_validation_registered_unvalidated(self):
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD)
        cfg['validation'] = True
        self.registry.notify(ptah.events.PrincipalRegisteredEvent(user))

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertFalse(props.validated)

    def test_validation_registered_no_validation(self):
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD)
        cfg['validation'] = False
        self.registry.notify(ptah.events.PrincipalRegisteredEvent(user))

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertTrue(props.validated)

    def test_validation_added(self):
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD)
        cfg['validation'] = False
        self.registry.notify(ptah.events.PrincipalAddedEvent(user))

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertTrue(props.validated)

        user = CrowdUser(title='name', login='login', email='email')
        cfg['validation'] = True
        self.registry.notify(ptah.events.PrincipalAddedEvent(user))

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertTrue(props.validated)

    def test_validation_initiate(self):
        from ptah_crowd import validation
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        origValidationTemplate = validation.ValidationTemplate

        class Stub(origValidationTemplate):

            status = ''
            token = None

            def send(self):
                Stub.status = 'Email has been sended'
                Stub.token = self.token

        validation.ValidationTemplate = Stub

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        validation.initiate_email_validation(user.email, user, self.request)
        self.assertEqual(Stub.status, 'Email has been sended')
        self.assertIsNotNone(Stub.token)

        t = ptah.token.service.get_bydata(validation.TOKEN_TYPE, user.__uri__)
        self.assertEqual(Stub.token, t)

        validation.ValidationTemplate = origValidationTemplate

    def test_validation_template(self):
        from ptah_crowd import validation
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        origValidationTemplate = validation.ValidationTemplate
        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        template = validation.ValidationTemplate(
            user, self.request, email = user.email, token = 'test-token')
        template.update()

        res = text_(template.render())

        self.assertIn(
            "You're close to completing the registration process.", res)
        self.assertIn(
            "http://example.com/validateaccount.html?token=test-token", res)

    def test_validate(self):
        from ptah_crowd import validation
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        t = ptah.token.service.generate(validation.TOKEN_TYPE, user.__uri__)

        res = validation.validate(self.request)
        self.assertIsInstance(res, HTTPFound)
        self.assertIn(
            "Can't validate email address.", ptah.render_messages(self.request))

        props = ptah_crowd.get_properties(user.__uri__)
        props.validated = False
        self.request.GET['token'] = t
        self.request.session.clear()

        res = validation.validate(self.request)
        self.assertIn("Account has been successfully validated.",
                      ptah.render_messages(self.request))

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertTrue(props.validated)
