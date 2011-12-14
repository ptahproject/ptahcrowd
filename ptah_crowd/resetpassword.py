""" reset password form """
from datetime import datetime
from ptah import config, form, view
from pyramid import security
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import mail
from ptah import auth_service
from ptah import pwd_tool
from ptah.password import PasswordSchema
from ptah.events import ResetPasswordInitiatedEvent
from ptah.events import PrincipalPasswordChangedEvent

from ptah_crowd.settings import _


@view_config(
    route_name='ptah-resetpassword',
    wrapper=ptah.wrap_layout('ptah-page'),
    renderer='ptah_crowd:templates/resetpassword.pt')

class ResetPassword(form.Form):

    fields = form.Fieldset(
        form.FieldFactory(
            'text',
            'login',
            title = _('Login Name'),
            description = _('Login names are not case sensitive.'),
            missing = '',
            default = ''))

    def form_content(self):
        return {'login': self.request.params.get('login', '')}

    def update(self):
        MAIL = ptah.get_settings(CFG_ID_MAIL)
        self.from_name = MAIL.from_name
        self.from_address = MAIL.from_address

        super(ResetPassword, self).update()

    @form.button(_('Start password reset'),name='reset',actype=form.AC_PRIMARY)
    def reset(self):
        request = self.request
        registry = request.registry
        data, errors = self.extract()

        login = data.get('login')
        if login:
            principal = auth_service.get_principal_bylogin(login)

            if principal is not None and pwd_tool.can_change_password(principal):
                passcode = pwd_tool.generate_passcode(principal)

                template = ResetPasswordTemplate(
                    principal, request, passcode = passcode)
                template.send()

                self.request.registry.notify(
                    ResetPasswordInitiatedEvent(principal))

                self.message(_('Password reseting process has been initiated. '
                               'Check your email for futher instructions.'))
                raise HTTPFound(location=request.application_url)

        self.message(_("System can't restore password for this user."))

    @form.button(_('Cancel'))
    def cancel(self):
        raise HTTPFound(location=self.request.application_url)


@view_config(
    route_name='ptah-resetpassword-form',
    wrapper=ptah.wrap_layout('ptah-page'),
    renderer='ptah_crowd:templates/resetpasswordform.pt')

class ResetPasswordForm(form.Form):

    fields = PasswordSchema

    def update(self):
        request = self.request

        passcode = request.subpath[0]
        self.principal = principal = pwd_tool.get_principal(passcode)

        if principal is not None and \
               pwd_tool.can_change_password(principal):
            self.passcode = passcode
            self.title = principal.name or principal.login
        else:
            self.message(_("Passcode is invalid."), 'warning')
            raise HTTPFound(
                location='%s/resetpassword.html'%request.application_url)

        super(ResetPasswordForm, self).update()

    @form.button(_("Change password"), name='change', actype=form.AC_PRIMARY)
    def changePassword(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
        else:
            principal = pwd_tool.get_principal(self.passcode)
            pwd_tool.change_password(self.passcode, data['password'])

            self.request.registry.notify(
                PrincipalPasswordChangedEvent(principal))

            # check if principal can be authenticated
            info = auth_service.authenticate_principal(principal)

            headers = []
            if info.status:
                headers = security.remember(self.request, info.__uri__)

            self.message(
                _('You have successfully changed your password.'), 'success')
            raise HTTPFound(
                headers = headers,
                location = self.request.application_url)


class ResetPasswordTemplate(mail.MailTemplate):

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

        self.to_address = mail.formataddr((info.name, info.login))
