import os, transaction
import ptah
from ptah import config
from ptah.authentication import AuthInfo
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest

import ptah_crowd


class Principal(object):

    def __init__(self, uri, name, login):
        self.__uri__ = uri
        self.name = name
        self.login = login


class TestValidation(PtahTestCase):

    def test_validation_auth_checker_validation(self):
        from ptah_crowd.validation import validationAndSuspendedChecker

        principal = Principal('1', 'user', 'user')

        props = ptah_crowd.get_properties(principal.__uri__)
        props.validated = False

        # validation disabled
        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['validation'] = False
        self.assertTrue(validationAndSuspendedChecker(info))
        transaction.commit()

        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['allow-unvalidated'] = False
        self.assertTrue(validationAndSuspendedChecker(info))
        transaction.commit()

        # validation enabled
        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['validation'] = True
        ptah_crowd.CONFIG['allow-unvalidated'] = False
        self.assertFalse(validationAndSuspendedChecker(info))
        self.assertEqual(info.message, 'Account is not validated.')
        transaction.commit()

        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['allow-unvalidated'] = True
        self.assertTrue(validationAndSuspendedChecker(info))
        transaction.commit()

        # validated
        props = ptah_crowd.get_properties(principal.__uri__)
        props.validated = True
        transaction.commit()

        info = AuthInfo(True, principal)
        ptah_crowd.CONFIG['validation'] = True
        self.assertTrue(validationAndSuspendedChecker(info))

    def test_validation_auth_checker_suspended(self):
        from ptah.authentication import AuthInfo
        from ptah_crowd.validation import validationAndSuspendedChecker

        principal = Principal('2', 'user', 'user')

        props = ptah_crowd.get_properties(principal.__uri__)
        props.validated = True
        props.suspended = False

        info = AuthInfo(True, principal)
        self.assertTrue(validationAndSuspendedChecker(info))

        props.suspended = True
        transaction.commit()

        info = AuthInfo(True, principal)
        self.assertFalse(validationAndSuspendedChecker(info))
        self.assertEqual(info.message, 'Account is suspended.')

    def test_validation_registered_unvalidated(self):
        from ptah_crowd.provider import CrowdUser

        user = CrowdUser('name', 'login', 'email')

        ptah_crowd.CONFIG['validation'] = True
        config.notify(ptah.events.PrincipalRegisteredEvent(user))

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertFalse(props.validated)

    def test_validation_registered_no_validation(self):
        from ptah_crowd.provider import CrowdUser

        user = CrowdUser('name', 'login', 'email')

        ptah_crowd.CONFIG['validation'] = False
        config.notify(ptah.events.PrincipalRegisteredEvent(user))

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertTrue(props.validated)

    def test_validation_added(self):
        from ptah_crowd.provider import CrowdUser

        user = CrowdUser('name', 'login', 'email')

        ptah_crowd.CONFIG['validation'] = False
        config.notify(ptah.events.PrincipalAddedEvent(user))

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertTrue(props.validated)

        user = CrowdUser('name', 'login', 'email')
        ptah_crowd.CONFIG['validation'] = True
        config.notify(ptah.events.PrincipalAddedEvent(user))

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertTrue(props.validated)

    def test_validation_initiate(self):
        from ptah_crowd import validation
        from ptah_crowd.provider import CrowdUser

        origValidationTemplate = validation.ValidationTemplate

        class Stub(origValidationTemplate):

            status = ''
            token = None

            def send(self):
                Stub.status = 'Email has been sended'
                Stub.token = self.token

        validation.ValidationTemplate = Stub

        user = CrowdUser('name', 'login', 'email')

        validation.initiate_email_validation(user.email, user, self.request)
        self.assertEqual(Stub.status, 'Email has been sended')
        self.assertIsNotNone(Stub.token)

        t = ptah.token.service.get_bydata(validation.TOKEN_TYPE, user.__uri__)
        self.assertEqual(Stub.token, t)

        validation.ValidationTemplate = origValidationTemplate

    def test_validation_template(self):
        from ptah_crowd import validation
        from ptah_crowd.provider import CrowdUser

        origValidationTemplate = validation.ValidationTemplate
        user = CrowdUser('name', 'login', 'email')

        template = validation.ValidationTemplate(
            user, self.request, email = user.email, token = 'test-token')
        template.update()

        res = template.render()

        self.assertIn(
            "You're close to completing the registration process.", res)
        self.assertIn(
            "http://example.com/validateaccount.html?token=test-token", res)

    def test_validate(self):
        from ptah_crowd import validation
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()

        t = ptah.token.service.generate(validation.TOKEN_TYPE, user.__uri__)

        try:
            validation.validate(self.request)
        except:
            pass
        self.assertIn(
            "Can't validate email address.",
            self.request.session['msgservice'][0])

        props = ptah_crowd.get_properties(user.__uri__)
        props.validated = False
        self.request.GET['token'] = t
        self.request.session.clear()

        try:
            validation.validate(self.request)
        except:
            pass
        self.assertIn(
            "Account has been successfully validated.",
            self.request.session['msgservice'][0])

        props = ptah_crowd.get_properties(user.__uri__)
        self.assertTrue(props.validated)
