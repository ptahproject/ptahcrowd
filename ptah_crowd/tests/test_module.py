import transaction
import ptah
from ptah import config
from ptah.testing import PtahTestCase
from webob.multidict import MultiDict
from pyramid.testing import DummyRequest
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

import ptah_crowd


class TestModule(PtahTestCase):

    def test_manage_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah_crowd.module import CrowdModule

        request = DummyRequest()

        ptah.authService.set_userid('test')
        ptah.manage.CONFIG['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['crowd']

        self.assertIsInstance(mod, CrowdModule)

    def test_manage_module_get(self):
        from ptah_crowd.module import CrowdModule, UserWrapper
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        uri = user.__uri__
        Session.add(user)
        Session.flush()

        mod = CrowdModule(None, DummyRequest())

        self.assertRaises(KeyError, mod.__getitem__, 'unkown')

        wu = mod[str(user.pid)]

        self.assertIsInstance(wu, UserWrapper)
        self.assertEqual(wu.user.__uri__, uri)


class TestModuleView(PtahTestCase):

    def _make_mod(self):
        from ptah_crowd.module import CrowdModule
        return CrowdModule(None, DummyRequest())

    def _make_user(self):
        from ptah_crowd.provider import CrowdUser, Session

        user = CrowdUser('name', 'login', 'email')
        Session.add(user)
        Session.flush()
        return user

    def test_module_search(self):
        from ptah_crowd.module import CrowdModuleView

        mod = self._make_mod()

        form = CrowdModuleView(mod, DummyRequest(
                POST=MultiDict({'form.buttons.search': 'Search',
                                'term': 'search term'})))
        form.csrf = False
        try:
            form.update()
        except Exception, res:
            pass

        self.assertIsInstance(res, HTTPFound)
        self.assertIn('ptah-search-term', form.request.session)
        self.assertEqual(
            form.request.session['ptah-search-term'], 'search term')

    def test_module_clear(self):
        from ptah_crowd.module import CrowdModuleView

        mod = self._make_mod()

        form = CrowdModuleView(mod, DummyRequest(
                session = {'ptah-search-term': 'test'},
                POST=MultiDict({'form.buttons.clear': 'Clear'})))
        form.csrf = False
        form.update()

        self.assertNotIn('ptah-search-term', form.request.session)

    def test_module_search_error(self):
        from ptah_crowd.module import CrowdModuleView

        mod = self._make_mod()

        form = CrowdModuleView(mod, DummyRequest(
                POST=MultiDict({'form.buttons.search': 'Search'})))
        form.csrf = False
        form.update()

        self.assertIn('Please specify search term',
                      form.request.session['msgservice'][0])

    def test_module_list(self):
        from ptah_crowd.module import CrowdModuleView

        mod = self._make_mod()
        user = self._make_user()

        res = CrowdModuleView.__renderer__(mod, DummyRequest(
                session = {'ptah-search-term': 'email'},
                params = MultiDict(), POST = MultiDict()))

        self.assertIn('value="%s"'%user.__uri__, res.body)

        res = CrowdModuleView.__renderer__(mod, DummyRequest(
                params = MultiDict(), POST = MultiDict()))

        self.assertIn('value="%s"'%user.__uri__, res.body)

        res = CrowdModuleView.__renderer__(mod, DummyRequest(
                params = MultiDict({'batch': 1}), POST = MultiDict()))

        self.assertIn('value="%s"'%user.__uri__, res.body)

        res = CrowdModuleView.__renderer__(mod, DummyRequest(
                params = MultiDict({'batch': 0}), POST = MultiDict()))

        self.assertIn('value="%s"'%user.__uri__, res.body)

    def test_module_validate(self):
        from ptah_crowd.module import CrowdModuleView
        from ptah_crowd.provider import Session

        mod = self._make_mod()
        user = self._make_user()
        uri = user.__uri__

        props = ptah_crowd.get_properties(uri)
        props.validated = False

        form = CrowdModuleView(mod, DummyRequest(
                POST=MultiDict(
                    {'uid': uri,
                     'validate': 'validate'})))

        form.csrf = False
        form.update()
        transaction.commit()

        self.assertIn('Selected accounts have been validated.',
                      form.request.session['msgservice'][0])
        props = ptah_crowd.get_properties(uri)
        self.assertTrue(props.validated)

    def test_module_suspend(self):
        from ptah_crowd.module import CrowdModuleView
        from ptah_crowd.provider import Session

        mod = self._make_mod()
        user = self._make_user()
        uri = user.__uri__

        props = ptah_crowd.get_properties(uri)
        props.suspended = False

        form = CrowdModuleView(mod, DummyRequest(
                POST=MultiDict(
                    {'uid': uri,
                     'suspend': 'suspend'})))

        form.csrf = False
        form.update()
        transaction.commit()

        self.assertIn('Selected accounts have been suspended.',
                      form.request.session['msgservice'][0])
        props = ptah_crowd.get_properties(uri)
        self.assertTrue(props.suspended)

    def test_module_activate(self):
        from ptah_crowd.module import CrowdModuleView
        from ptah_crowd.provider import Session

        mod = self._make_mod()
        user = self._make_user()
        uri = user.__uri__

        props = ptah_crowd.get_properties(uri)
        props.suspended = True

        form = CrowdModuleView(mod, DummyRequest(
                POST=MultiDict(
                    {'uid': uri,
                     'activate': 'activate'})))

        form.csrf = False
        form.update()
        transaction.commit()

        self.assertIn('Selected accounts have been activated.',
                      form.request.session['msgservice'][0])
        props = ptah_crowd.get_properties(uri)
        self.assertFalse(props.suspended)
