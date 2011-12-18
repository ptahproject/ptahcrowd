""" role """
import transaction
import ptah, ptah_crowd
from ptah import config
from ptah.testing import PtahTestCase


class TestCrowdApplication(PtahTestCase):

    def test_crowd_factory(self):
        import ptah_crowd

        factory = ptah_crowd.CrowdFactory()
        self.assertEqual(factory.__name__, ptah_crowd.CROWD_APP_ID)
        self.assertIsInstance(factory, ptah_crowd.CrowdApplication)

    def test_crowd_app_add_user(self):
        import ptah_crowd

        factory = ptah_crowd.CrowdFactory()

        user = ptah_crowd.CrowdUser()
        factory.add(user)

        self.assertEqual(user.__name__, str(user.__id__))

    def test_crowd_allowed(self):
        from ptah_crowd.provider import get_allowed_content_types

        self.assertEqual(get_allowed_content_types(None), ('ptah-crowd-user',))


class TestProvider(PtahTestCase):

    def test_authenticate(self):
        from ptah_crowd.provider import \
             CrowdAuthProvider, CrowdFactory, CrowdUser

        provider = CrowdAuthProvider()

        self.assertFalse(
            provider.authenticate(
                {'login': 'test', 'password': '12345'}))

        user = CrowdUser(title='test',
                         login='test',
                         email='test@ptahproject.org',
                         password=ptah.pwd_tool.encode('12345'))
        factory = CrowdFactory()
        factory.add(user)

        self.assertTrue(
            provider.authenticate(
                {'login': 'test', 'password': '12345'}))

        self.assertFalse(
            provider.authenticate(
                {'login': 'test', 'password': '56789'}))


    def test_get_bylogin(self):
        from ptah_crowd.provider import \
             CrowdAuthProvider, CrowdFactory, CrowdUser

        provider = CrowdAuthProvider()
        self.assertIsNone(provider.get_principal_bylogin('test'))

        user = CrowdUser(title='test', login='test',
                         email='test@ptahproject.org',
                         password=ptah.pwd_tool.encode('12345'))
        CrowdFactory().add(user)

        user = provider.get_principal_bylogin('test')
        self.assertIsInstance(user, CrowdUser)
        self.assertEqual(user.login, 'test')

    def test_crowd_user_ctor(self):
        from ptah_crowd.provider import CrowdUser

        user = CrowdUser(title='user-name', login='user-login',
                         email='user-email', password='passwd')

        self.assertEqual(user.title, 'user-name')
        self.assertEqual(user.login, 'user-login')
        self.assertEqual(user.email, 'user-email')
        self.assertEqual(user.password, 'passwd')
        self.assertTrue(user.__uri__.startswith('cms-ptah-crowd-user'))
        self.assertEqual(str(user), 'user-name')
        self.assertEqual(repr(user), 'CrowdUser<%s:%s>'%(
            user.name, user.__uri__))

    def test_crowd_user_change_password(self):
        from ptah_crowd.provider import CrowdUser, CrowdAuthProvider

        user = CrowdUser(title='user-name', login='user-login',
                         email='user-email', password='passwd')

        CrowdAuthProvider.change_password(user, '123456')
        self.assertEqual(user.password, '123456')

    def test_crowd_user_change_search(self):
        from ptah_crowd.provider import \
             CrowdUser, CrowdFactory, CrowdAuthProvider

        user = CrowdUser(title='user-name', login='user-login',
                         email='user-email', password='passwd')
        uri = user.__uri__

        CrowdFactory().add(user)

        users = list(CrowdAuthProvider.search('user'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].__uri__, uri)

        users = list(CrowdAuthProvider.search('email'))
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].__uri__, uri)


class TestPasswordChanger(PtahTestCase):

    def test_password_changer(self):
        from ptah_crowd.provider import CrowdUser

        app = self.config.make_wsgi_app()

        user = CrowdUser(title='user-name', login='user-login',
                         email='user-email', password='passwd')

        self.assertTrue(ptah.pwd_tool.can_change_password(user))
