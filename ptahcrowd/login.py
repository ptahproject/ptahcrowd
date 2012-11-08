""" login form """
import ptah
import pform
from pyramid import security
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptahcrowd
from ptahcrowd import const
from ptahcrowd.settings import _, CFG_ID_CROWD


@view_config(
    route_name='ptah-login',
    wrapper=ptah.wrap_layout('crowd'),
    renderer="ptah-crowd:login.lt")
class LoginForm(pform.Form, ptah.View):
    """ Login form """

    id = 'login-form'
    title = _('Login')

    fields = pform.Fieldset(
        pform.fields.TextField(
            'login',
            title=const.LOGIN_TITLE,
            description=const.CASE_WARN,
            default=''),

        pform.fields.PasswordField(
            'password',
            title=const.PASSWORD_TITLE,
            description=const.CASE_WARN,
            default=''),
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
                location = '%s%s' % (app_url, location)
        else:
            location = self.request.route_url('ptah-login-success')

        return location

    @pform.button(_("Log in"), name='login', actype=pform.AC_PRIMARY)
    def login_handler(self):
        request = self.request

        data, errors = self.extract()
        if errors:
            self.add_error_message(errors)
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
            self.request.add_message(info.message, 'warning')
            return

        self.request.add_message(const.WRONG_CREDENTIALS, 'error')

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

        cfg = ptah.get_settings(ptahcrowd.CFG_ID_AUTH, self.request.registry)
        self.providers = cfg['providers']

        return super(LoginForm, self).update()


@view_config(
    route_name='ptah-login-success',
    wrapper=ptah.wrap_layout('crowd'),
    renderer='ptah-crowd:login-success.lt')
class LoginSuccess(ptah.View):
    """ Login successful information page. """

    def update(self):
        user = ptah.auth_service.get_current_principal()
        if user is None:
            request = self.request
            headers = security.forget(request)

            return HTTPFound(
                headers=headers,
                location='%s/login.html' % request.application_url)
        else:
            self.user = user.name or user.login


@view_config(
    route_name='ptah-login-suspended', wrapper=ptah.wrap_layout('crowd'),
    renderer="ptah-crowd:login-suspended.lt")
class LoginSuspended(ptah.View):
    """ Suspended account information page. """

    def update(self):
        principal = ptah.auth_service.get_current_principal()
        if not principal:
            return HTTPFound(location=self.request.application_url)

        if not principal.suspended:
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

        request.add_message(const.LOGOUT_SUCCESSFUL, 'info')
        headers = security.forget(request)
        return HTTPFound(
            headers=headers,
            location=request.application_url)
    else:
        return HTTPFound(location=request.application_url)
