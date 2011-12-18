""" account validation/suspending """
from datetime import timedelta, datetime
from pyramid.view import view_config
from pyramid.compat import text_type
from pyramid.security import remember
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import mail

from ptah_crowd.settings import CFG_ID_CROWD
from ptah_crowd.memberprops import get_properties, query_properties

TOKEN_TYPE = ptah.token.TokenType(
    'cd51f14e9b2842608ccadf1a240046c1', timedelta(hours=24))


def initiate_email_validation(email, principal, request):
    """ initiate principal email validation """
    t = ptah.token.service.generate(TOKEN_TYPE, principal.__uri__)
    template = ValidationTemplate(principal, request, email=email, token = t)
    template.send()


@ptah.auth_checker
def validationAndSuspendedChecker(info):
    props = get_properties(info.__uri__)
    if props.suspended:
        info.message = 'Account is suspended.'
        info.arguments['suspended'] = True
        return False

    if props.validated:
        return True

    CROWD = ptah.get_settings(CFG_ID_CROWD)
    if not CROWD['validation']:
        return True

    if CROWD['allow-unvalidated'] or props.validated:
        return True

    info.message = 'Account is not validated.'
    info.arguments['validation'] = False
    return False


@ptah.subscriber(ptah.events.PrincipalRegisteredEvent)
def principalRegistered(ev):
    props = get_properties(ev.principal.__uri__)
    props.joined = datetime.now()

    cfg = ptah.get_settings(CFG_ID_CROWD)
    if not cfg['validation']:
        props.validated = True


@ptah.subscriber(ptah.events.PrincipalAddedEvent)
def principalAdded(ev):
    props = get_properties(ev.principal.__uri__)
    props.joined = datetime.now()
    props.validated = True


class ValidationTemplate(mail.MailTemplate):

    subject = 'Activate Your Account'
    template = 'ptah_crowd:templates/validate_email.txt'

    def update(self):
        super(ValidationTemplate, self).update()

        self.url = '%s/validateaccount.html?token=%s'%(
            self.request.application_url, self.token)

        principal = self.context
        self.to_address = mail.formataddr((principal.name, self.email))


@view_config(route_name='ptah-principal-validate')
def validate(request):
    """Validate account"""
    t = request.GET.get('token')

    data = ptah.token.service.get(t)
    if data is not None:
        props = query_properties(data)
        if props is not None:
            props.validated = True
            ptah.token.service.remove(t)
            ptah.add_message(request,"Account has been successfully validated.")

            request.registry.notify(
                ptah.events.PrincipalValidatedEvent(ptah.resolve(props.uri)))

            headers = remember(request, props.uri)
            return HTTPFound(location=request.application_url, headers=headers)

    ptah.add_message(request, "Can't validate email address.", 'warning')
    return HTTPFound(location=request.application_url)
