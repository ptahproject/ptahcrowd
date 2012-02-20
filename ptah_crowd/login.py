""" login form """
import ptah
from ptah import view, form
from pyramid import security
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptah_crowd
from ptah_crowd.settings import _, CFG_ID_CROWD
from ptah_crowd.memberprops import get_properties


@view_config(
    route_name='ptah-login',
    wrapper=ptah.wrap_layout('ptah-page'),
    renderer="ptah_crowd:templates/login.pt")

class LoginForm(form.Form):
    """ Login form """

    id = 'login-form'
    title = _('Login')

    fields = form.Fieldset(
        form.fields.TextField(
            'login',
            title = _('Login Name'),
            description = _('Login names are case sensitive, '\
                                'make sure the caps lock key is not enabled.'),
            default = ''),

        form.fields.PasswordField(
            'password',
            title = _('Password'),
            description = _('Case sensitive, make sure caps '\
                                'lock is not enabled.'),
            default = ''),
        )

    def get_success_url(self):
        app_url = self.application_url
        cfg = ptah.get_settings(CFG_ID_CROWD, self.request.registry)

        came_from = self.request.GET.get('came_from', '')
        if came_from.startswith(app_url):
            location = came_from
        elif cfg['success-url']:
            location = cfg['success-url']
            if location.startswith('/'):
                location = '%s%s'%(app_url, location)
        else:
            location = self.request.route_url('ptah-login-success')

        return location

    @form.button(_("Log in"), name='login', actype=form.AC_PRIMARY)
    def login_handler(self):
        request = self.request

        data, errors = self.extract()
        if errors:
            self.message(errors, 'form-error')
            return

        info = ptah.auth_service.authenticate(data)

        if info.status:
            request.registry.notify(
                ptah.events.LoggedInEvent(info.principal))

            headers = security.remember(request, info.__uri__)
            return HTTPFound(headers=headers, location=self.get_success_url())

        if info.principal is not None:
            request.registry.notify(
                ptah.events.LoginFailedEvent(info.principal, info.message))

        if info.arguments.get('suspended'):
            return HTTPFound(request.route_url('ptah-login-suspended'))

        if info.message:
            self.message(info.message, 'warning')
            return

        self.message(_('You enter wrong login or password.'), 'error')

    def update(self):
        cfg = ptah.get_settings(CFG_ID_CROWD, self.request.registry)

        self.app_url = self.application_url
        self.join = cfg['join']
        joinurl = cfg['join-url']
        if joinurl:
            self.joinurl = joinurl
        else:
            self.joinurl = self.request.route_url('ptah-join')

        if ptah.auth_service.get_userid():
            return HTTPFound(location=self.get_success_url())

        cfg = ptah.get_settings(ptah_crowd.CFG_ID_AUTH, self.request.registry)
        self.providers = cfg['providers']

        return super(LoginForm, self).update()


@view_config(
    route_name='ptah-login-success', wrapper=ptah.wrap_layout('ptah-page'),
    renderer='ptah_crowd:templates/login-success.pt')

class LoginSuccess(ptah.View):
    """ Login successful information page. """

    def update(self):
        user = ptah.auth_service.get_current_principal()
        if user is None:
            request = self.request
            headers = security.forget(request)

            return HTTPFound(
                headers = headers,
                location = '%s/login.html'%request.application_url)
        else:
            self.user = user.name or user.login


@view_config(
    route_name='ptah-login-suspended', wrapper=ptah.wrap_layout('ptah-page'),
    renderer="ptah_crowd:templates/login-suspended.pt")

class LoginSuspended(ptah.View):
    """ Suspended account information page. """

    def update(self):
        uid = ptah.auth_service.get_userid()
        if not uid:
            return HTTPFound(location=self.request.application_url)

        props = get_properties(uid)
        if not props.suspended:
            return HTTPFound(location=self.request.application_url)

        MAIL = ptah.get_settings(ptah.CFG_ID_PTAH)
        self.from_name = MAIL['email_from_name']
        self.from_address = MAIL['email_from_address']
        self.full_address = MAIL['full_email_address']


@view_config(route_name='ptah-logout')
def logout(request):
    """Logout action"""
    uid = ptah.auth_service.get_userid()

    if uid is not None:
        ptah.auth_service.set_userid(None)
        request.registry.notify(
            ptah.events.LoggedOutEvent(ptah.resolve(uid)))

        view.add_message(request, _('Logout successful!'), 'info')
        headers = security.forget(request)
        return HTTPFound(
            headers = headers,
            location = request.application_url)
    else:
        return HTTPFound(location = request.application_url)
