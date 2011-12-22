import transaction
import ptah
from ptah import config
from ptah.testing import PtahTestCase
from webob.multidict import MultiDict
from pyramid.testing import DummyRequest
from pyramid.view import render_view_to_response
from pyramid.httpexceptions import HTTPFound, HTTPForbidden

import ptah_crowd


class TestModule(PtahTestCase):

    def test_manage_module(self):
        from ptah.manage.manage import PtahManageRoute
        from ptah_crowd.module import CrowdModule

        request = DummyRequest()

        ptah.auth_service.set_userid('test')

        cfg = ptah.get_settings(ptah.CFG_ID_PTAH)
        cfg['managers'] = ('*',)
        mr = PtahManageRoute(request)
        mod = mr['crowd']

        self.assertIsInstance(mod, CrowdModule)

    def test_manage_module_get(self):
        from ptah_crowd.module import CrowdModule
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        uri = user.__uri__

        mod = CrowdModule(None, DummyRequest())

        self.assertRaises(KeyError, mod.__getitem__, 'unkown')

        wu = mod[str(user.__id__)]

        self.assertIsInstance(wu, CrowdUser)
        self.assertEqual(wu.__uri__, uri)


class TestModuleView(PtahTestCase):

    def _make_mod(self):
        from ptah_crowd.module import CrowdModule
        return CrowdModule(None, DummyRequest())

    def _make_user(self):
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)
        return user

    def test_module_search(self):
        from ptah_crowd.views import CrowdApplicationView

        mod = self._make_mod()

        form = CrowdApplicationView(mod, DummyRequest(
                POST=MultiDict((('form.buttons.search', 'Search'),
                                ('term', 'search term')))))
        form.csrf = False
        res = form.update()

        self.assertIn('ptah-search-term', form.request.session)
        self.assertEqual(
            form.request.session['ptah-search-term'], 'search term')

    def test_module_clear(self):
        from ptah_crowd.views import CrowdApplicationView

        mod = self._make_mod()

        form = CrowdApplicationView(mod, DummyRequest(
                session = {'ptah-search-term': 'test'},
                POST=MultiDict((('form.buttons.clear', 'Clear'),))))
        form.csrf = False
        form.update()

        self.assertNotIn('ptah-search-term', form.request.session)

    def test_module_search_error(self):
        from ptah_crowd.views import CrowdApplicationView

        mod = self._make_mod()

        form = CrowdApplicationView(mod, DummyRequest(
                POST=MultiDict((('form.buttons.search', 'Search'),))))
        form.csrf = False
        form.update()

        self.assertIn('Please specify search term',
                      ptah.render_messages(form.request))

    def test_module_list(self):
        from ptah_crowd.views import CrowdApplicationView

        mod = self._make_mod()
        user = self._make_user()

        request = DummyRequest(
            params = MultiDict(), POST = MultiDict())
        request.session['ptah-search-term'] = 'email'

        res = render_view_to_response(mod, request, '')

        self.assertIn('value="%s"'%user.__uri__, res.text)

        res = render_view_to_response(
            mod,
            DummyRequest(params = MultiDict(), POST = MultiDict()), '')

        self.assertIn('value="%s"'%user.__uri__, res.text)

        res = render_view_to_response(
            mod,
            DummyRequest(params = MultiDict({'batch': 1}),
                         POST = MultiDict()), '')

        self.assertIn('value="%s"'%user.__uri__, res.text)

        res = render_view_to_response(
            mod,
            DummyRequest(params = MultiDict({'batch': 0}),
                         POST = MultiDict()), '')

        self.assertIn('value="%s"'%user.__uri__, res.text)

    def test_module_validate(self):
        from ptah_crowd.views import CrowdApplicationView

        mod = self._make_mod()
        user = self._make_user()
        uri = user.__uri__

        props = ptah_crowd.get_properties(uri)
        props.validated = False

        form = CrowdApplicationView(mod, DummyRequest(
                POST=MultiDict((('uid', uri),
                                ('validate', 'validate')))))

        form.csrf = False
        form.update()
        transaction.commit()

        self.assertIn('Selected accounts have been validated.',
                      ptah.render_messages(form.request))
        props = ptah_crowd.get_properties(uri)
        self.assertTrue(props.validated)

    def test_module_suspend(self):
        from ptah_crowd.views import CrowdApplicationView

        mod = self._make_mod()
        user = self._make_user()
        uri = user.__uri__

        props = ptah_crowd.get_properties(uri)
        props.suspended = False

        form = CrowdApplicationView(mod, DummyRequest(
                POST=MultiDict((('uid', uri),
                                ('suspend', 'suspend')))))
        form.request.POST[form.csrfname] = form.request.session.get_csrf_token()
        form.update()

        self.assertIn('Selected accounts have been suspended.',
                      ptah.render_messages(form.request))
        transaction.commit()
        props = ptah_crowd.get_properties(uri)
        self.assertTrue(props.suspended)

    def test_module_activate(self):
        from ptah_crowd.views import CrowdApplicationView

        mod = self._make_mod()
        user = self._make_user()
        uri = user.__uri__

        props = ptah_crowd.get_properties(uri)
        props.suspended = True

        form = CrowdApplicationView(mod, DummyRequest(
                POST=MultiDict((('uid', uri),
                                ('activate', 'activate')))))

        form.csrf = False
        form.update()
        transaction.commit()

        self.assertIn('Selected accounts have been activated.',
                      ptah.render_messages(form.request))
        props = ptah_crowd.get_properties(uri)
        self.assertFalse(props.suspended)

    def test_module_remove(self):
        from ptah_crowd.views import CrowdApplicationView

        mod = self._make_mod()
        user = self._make_user()
        uri = user.__uri__

        props = ptah_crowd.get_properties(uri)
        props.suspended = False

        form = CrowdApplicationView(mod, DummyRequest(
                POST=MultiDict((('uid', uri),
                                ('remove', 'remove')))))
        form.update()

        self.assertIn('Selected accounts have been removed.',
                      ptah.render_messages(form.request))
        transaction.commit()

        user = ptah.resolve(user.__uri__)
        self.assertIsNone(user)
