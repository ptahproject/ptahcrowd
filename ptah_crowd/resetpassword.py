""" reset password form """
import ptah
from datetime import datetime
from pyramid import security
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

from ptah.password import PasswordSchema
from ptah.events import ResetPasswordInitiatedEvent
from ptah.events import PrincipalPasswordChangedEvent

from ptah_crowd.settings import _


@view_config(
    route_name='ptah-resetpassword',
    wrapper=ptah.wrap_layout('ptah-page'),
    renderer='ptah_crowd:templates/resetpassword.pt')

class ResetPassword(ptah.form.Form):

    fields = ptah.form.Fieldset(
        ptah.form.FieldFactory(
            'text',
            'login',
            title = _('Login Name'),
            description = _('Login names are not case sensitive.'),
            missing = '',
            default = ''))

    def form_content(self):
        return {'login': self.request.params.get('login', '')}

    def update(self):
        cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.request.registry)
        self.from_name = cfg['email_from_name']
        self.from_address = cfg['email_from_address']

        return super(ResetPassword, self).update()

    @ptah.form.button(_('Start password reset'),
                      name='reset', actype=ptah.form.AC_PRIMARY)
    def reset(self):
        request = self.request
        registry = request.registry
        data, errors = self.extract()

        login = data.get('login')
        if login:
            principal = ptah.auth_service.get_principal_bylogin(login)

            if principal is not None and \
                   ptah.pwd_tool.can_change_password(principal):
                passcode = ptah.pwd_tool.generate_passcode(principal)

                template = ResetPasswordTemplate(
                    principal, request, passcode = passcode)
                template.send()

                self.request.registry.notify(
                    ResetPasswordInitiatedEvent(principal))

                self.message(_('Password reseting process has been initiated. '
                               'Check your email for futher instructions.'))
                return HTTPFound(location=request.application_url)

        self.message(_("System can't restore password for this user."))

    @ptah.form.button(_('Cancel'))
    def cancel(self):
        return HTTPFound(location=self.request.application_url)


@view_config(
    route_name='ptah-resetpassword-form',
    wrapper=ptah.wrap_layout('ptah-page'),
    renderer='ptah_crowd:templates/resetpasswordform.pt')

class ResetPasswordForm(ptah.form.Form):

    fields = PasswordSchema

    def update(self):
        request = self.request

        passcode = request.subpath[0]
        self.principal = principal = ptah.pwd_tool.get_principal(passcode)

        if principal is not None and \
               ptah.pwd_tool.can_change_password(principal):
            self.passcode = passcode
            self.title = principal.name or principal.login
        else:
            self.message(_("Passcode is invalid."), 'warning')
            return HTTPFound(
                location='%s/resetpassword.html'%request.application_url)

        return super(ResetPasswordForm, self).update()

    @ptah.form.button(_("Change password"),
                      name='change', actype=ptah.form.AC_PRIMARY)
    def changePassword(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
        else:
            principal = ptah.pwd_tool.get_principal(self.passcode)
            ptah.pwd_tool.change_password(self.passcode, data['password'])

            self.request.registry.notify(
                PrincipalPasswordChangedEvent(principal))

            # check if principal can be authenticated
            info = ptah.auth_service.authenticate_principal(principal)

            headers = []
            if info.status:
                headers = security.remember(self.request, info.__uri__)

            self.message(
                _('You have successfully changed your password.'), 'success')
            return HTTPFound(
                headers = headers,
                location = self.request.application_url)


class ResetPasswordTemplate(ptah.mail.MailTemplate):

    subject = 'Password Reset Confirmation'
    template = 'ptah_crowd:templates/resetpasswordmail.pt'

    def update(self):
        super(ResetPasswordTemplate, self).update()

        request = self.request

        self.date = datetime.now()

        remoteAddr = request.get('REMOTE_ADDR', '')
        forwardedFor = request.get('HTTP_X_FORWARDED_FOR', None)

        self.from_ip = (forwardedFor and '%s/%s' %
                        (remoteAddr, forwardedFor) or remoteAddr)

        self.url = '%s/resetpassword.html/%s/'%(
            request.application_url, self.passcode)

        info = self.context

        self.to_address = ptah.mail.formataddr((info.name, info.login))
