""" role """
import transaction
import ptah, ptah_crowd
from ptah import config
from ptah.testing import PtahTestCase


class TestProvider(PtahTestCase):

    def test_authenticate(self):
        from ptah_crowd.provider import CrowdProvider, CrowdUser, Session

        provider = CrowdProvider()

        self.assertFalse(
            provider.authenticate(
                {'login': 'test', 'password': '12345'}))

        user = CrowdUser('test', 'test', 'test@ptahproject.org',
                         ptah.pwd_tool.encode('12345'))
        Session.add(user)
        transaction.commit()

        self.assertTrue(
            provider.authenticate(
                {'login': 'test', 'password': '12345'}))

        self.assertFalse(
            provider.authenticate(
                {'login': 'test', 'password': '56789'}))


    def test_get_bylogin(self):
        from ptah_crowd.provider import CrowdProvider, CrowdUser, Session

        provider = CrowdProvider()

        self.assertIsNone(provider.get_principal_bylogin('test'))

        user = CrowdUser('test', 'test', 'test@ptahproject.org',
                         ptah.pwd_tool.encode('12345'))
        Session.add(user)
        transaction.commit()

        user = provider.get_principal_bylogin('test')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.login, 'test')

    def test_crowd_user_ctor(self):
        from ptah_crowd.provider import CrowdUser

        user = CrowdUser('user-name', 'user-login', 'user-email', 'passwd')

        self.assertEqual(user.name, 'user-name')
        self.assertEqual(user.login, 'user-login')
        self.assertEqual(user.email, 'user-email')
        self.assertEqual(user.password, 'passwd')
        self.assertTrue(user.__uri__.startswith('user-crowd'))
        self.assertEqual(str(user), 'user-name')
        self.assertEqual(repr(user), 'CrowdUser<%s:%s>'%(user.name, user.__uri__))

    def test_crowd_user_get(self):
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('user-name', 'user-login', 'user-email', 'passwd')
        uri = user.__uri__

        Session.add(user)
        Session.flush()

        self.assertEqual(CrowdUser.get(user.pid).__uri__, uri)
        self.assertEqual(CrowdUser.get_byuri(user.__uri__).__uri__, uri)
        self.assertEqual(CrowdUser.get_bylogin(user.login).__uri__, uri)

    def test_crowd_user_change_password(self):
        from ptah_crowd.provider import CrowdUser, change_pwd

        user = CrowdUser('user-name', 'user-login', 'user-email', 'passwd')
        uri = user.__uri__

        change_pwd(user, '123456')
        self.assertEqual(user.password, '123456')

    def test_crowd_user_change_search(self):
        from ptah_crowd.provider import Session, CrowdUser, search

        user = CrowdUser('user-name', 'user-login', 'user-email', 'passwd')
        uri = user.__uri__

        Session.add(user)
        Session.flush()

        users = list(search('user'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].__uri__, uri)

        users = list(search('email'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].__uri__, uri)
