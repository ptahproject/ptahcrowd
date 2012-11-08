""" account validation/suspending """
from datetime import timedelta, datetime
from pyramid.view import view_config
from pyramid.security import remember
from pyramid.httpexceptions import HTTPFound

import ptah
from ptahcrowd.settings import CFG_ID_CROWD

TOKEN_TYPE = ptah.token.TokenType(
    'cd51f14e9b2842608ccadf1a240046c1', timedelta(hours=24))


def initiate_email_validation(email, principal, request):
    """ Initiate email validation

    :param email: email address of user
    :param principal: principal object
    :param request: current request object
    """
    t = ptah.token.service.generate(TOKEN_TYPE, principal.__uri__)
    template = ValidationTemplate(principal, request, email=email, token = t)
    template.send()


@ptah.auth_checker
def validationAndSuspendedChecker(info):
    principal = info.principal

    if principal.suspended:
        info.message = 'Account is suspended.'
        info.arguments['suspended'] = True
        return False

    if principal.validated:
        return True

    CROWD = ptah.get_settings(CFG_ID_CROWD)
    if not CROWD['validation']:
        return True

    if CROWD['allow-unvalidated'] or principal.validated:
        return True

    info.message = 'Account is not validated.'
    info.arguments['validation'] = False
    return False


@ptah.subscriber(ptah.events.PrincipalRegisteredEvent)
def principalRegistered(ev):
    ev.principal.joined = datetime.now()

    cfg = ptah.get_settings(CFG_ID_CROWD)
    if not cfg['validation']:
        ev.principal.validated = True


class ValidationTemplate(ptah.mail.MailTemplate):

    subject = 'Activate Your Account'
    template = 'ptahcrowd:templates/validate_email.txt'

    def update(self):
        super(ValidationTemplate, self).update()

        self.url = '%s/validateaccount.html?token=%s'%(
            self.request.application_url, self.token)

        principal = self.context
        self.to_address = ptah.mail.formataddr((principal.name, self.email))


@view_config(route_name='ptah-principal-validate')
def validate(request):
    """Validate account"""
    t = request.GET.get('token')

    data = ptah.token.service.get(t)
    if data is not None:
        user = ptah.resolve(data)
        if user is not None:
            user.validated = True
            ptah.token.service.remove(t)
            request.add_message("Account has been successfully validated.")

            request.registry.notify(ptah.events.PrincipalValidatedEvent(user))

            headers = remember(request, user.__uri__)
            return HTTPFound(location=request.application_url, headers=headers)

    request.add_message("Can't validate email address.", 'warning')
    return HTTPFound(location=request.application_url)
