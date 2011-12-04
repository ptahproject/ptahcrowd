""" login form """
import ptah
from ptah import view, form
from pyramid import security
from pyramid.httpexceptions import HTTPFound

from ptah_crowd.settings import _, CFG_ID_CROWD
from ptah_crowd.memberprops import get_properties

view.register_route(
    'ptah-login', '/login.html', use_global_views=True)
view.register_route(
    'ptah-logout', '/logout.html', use_global_views=True)
view.register_route(
    'ptah-login-success', '/login-success.html', use_global_views=True)
view.register_route(
    'ptah-login-suspended', '/login-suspended.html', use_global_views=True)


class LoginForm(form.Form):
    view.pview(
        route='ptah-login', layout='ptah-page',
        template = view.template("ptah_crowd:templates/login.pt"))

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

    @form.button(_("Log in"), name='login', actype=form.AC_PRIMARY)
    def handleLogin(self):
        request = self.request

        data, errors = self.extract()
        if errors:
            self.message(errors, 'form-error')
            return

        info = ptah.auth_service.authenticate(data)

        if info.status:
            request.registry.notify(
                ptah.events.LoggedInEvent(info.principal))

            location = request.application_url

            came_from = request.GET.get('came_from', '')
            if came_from.startswith(location):
                location = came_from
            else:
                location = '%s/login-success.html'%location

            headers = security.remember(request, info.__uri__)
            raise HTTPFound(headers = headers, location = location)

        if info.principal is not None:
            request.registry.notify(
                ptah.events.LoginFailedEvent(info.principal, info.message))

        if info.arguments.get('suspended'):
            raise HTTPFound(
                location='%s/login-suspended.html'%request.application_url)

        if info.message:
            self.message(info.message, 'warning')
            return

        self.message(_('You enter wrong login or password.'), 'error')

    def update(self):
        self.app_url = self.request.application_url
        cfg = ptah.get_settings(CFG_ID_CROWD, self.request.registry)
        self.join = cfg['join']
        if cfg['joinurl']:
            self.joinurl = cfg['joinurl']
        else:
            self.joinurl = '%s/join.html'%self.app_url

        if ptah.auth_service.get_userid():
            raise HTTPFound(location = '%s/login-success.html'%self.app_url)

        super(LoginForm, self).update()


class LoginSuccess(view.View):
    """ Login successful information page. """

    view.pview(
        route = 'ptah-login-success', layout='ptah-page',
        template = view.template("ptah_crowd:templates/login-success.pt"))

    def update(self):
        user = ptah.auth_service.get_current_principal()
        if user is None:
            request = self.request
            headers = security.forget(request)

            raise HTTPFound(
                headers = headers,
                location = '%s/login.html'%request.application_url)
        else:
            self.user = user.name or user.login


class LoginSuspended(view.View):
    """ Suspended account information page. """

    view.pview(
        route = 'ptah-login-suspended', layout='ptah-page',
        template = view.template("ptah_crowd:templates/login-suspended.pt"))

    def update(self):
        uid = ptah.auth_service.get_userid()
        if not uid:
            raise HTTPFound(location=self.request.application_url)

        props = get_properties(uid)
        if not props.suspended:
            raise HTTPFound(location=self.request.application_url)

        MAIL = ptah.get_settings(ptah.CFG_ID_MAIL)
        self.from_name = MAIL.from_name
        self.from_address = MAIL.from_address
        self.full_address = ptah.mail.formataddr(
            (MAIL.from_name, MAIL.from_address))


@view.pview(route='ptah-logout')
def logout(request):
    """Logout action"""
    uid = ptah.auth_service.get_userid()

    if uid is not None:
        ptah.auth_service.set_userid(None)
        request.registry.notify(
            ptah.events.LoggedOutEvent(ptah.resolve(uid)))

        view.add_message(request, _('Logout successful!'), 'info')
        headers = security.forget(request)
        raise HTTPFound(
            headers = headers,
            location = request.application_url)
    else:
        raise HTTPFound(location = request.application_url)
