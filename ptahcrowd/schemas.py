""" schemas """
import pform
from pyramid.compat import string_types

import ptah
from ptah.password import passwordValidator

from ptahcrowd import const
from ptahcrowd.settings import _


def lower(s):
    if isinstance(s, string_types):
        return s.lower()
    return s


def checkUsernameValidator(field, username):
    """Ptah field validator, checks if username is already in use."""

    if getattr(field, 'value', None) == username:
        return

    if ptah.auth_service.get_principal_byusername(username) is not None:
        raise pform.Invalid(_("This login is already in use."), field)

def checkEmailValidator(field, email):
    """Ptah field validator, checks if email is already in use."""

    if getattr(field, 'value', None) == email:
        return

    if ptah.auth_service.get_principal_byemail(email) is not None:
        raise pform.Invalid(_("This email is already in use."), field)


RegistrationSchema = pform.Fieldset(

    pform.TextField(
        'username',
        title=const.USERNAME_TITLE,
        description=const.USERNAME_DESCR,
        validator=checkUsernameValidator,
        ),

    pform.TextField(
        'email',
        title=const.EMAIL_TITLE,
        description=const.EMAIL_DESCR,
        preparer=lower,
        validator=pform.All(pform.Email(), checkEmailValidator),
        )
    )


ResetPasswordSchema = pform.Fieldset(

    pform.TextField(
        'login',
        title=const.LOGIN_TITLE,
        description=' '.join([const.LOGIN_DESCR, const.CASE_DESCR]),
        missing='',
        default='')
    )


UserSchema = pform.Fieldset(

    pform.fields.TextField(
        'fullname',
        title=const.FULLNAME_TITLE,
        description=const.FULLNAME_DESCR,
        required=False
        ),

    pform.fields.TextField(
        'username',
        title=const.USERNAME_TITLE,
        description=const.USERNAME_DESCR,
        validator=checkUsernameValidator,
        ),

    pform.fields.TextField(
        'email',
        title=const.EMAIL_TITLE,
        description=const.EMAIL_DESCR,
        preparer=lower,
        validator=pform.All(pform.Email(), checkEmailValidator),
        ),

    pform.fields.TextField(
        'password',
        title=const.PASSWORD_TITLE,
        description=const.PASSWORD_DESCR,
        validator=passwordValidator),

    pform.fields.BoolField(
        'validated',
        title=_('Validated'),
        default=True,
        ),

    pform.fields.BoolField(
        'suspended',
        title=_('Suspended'),
        default=False,
        ),

    )


ManagerChangePasswordSchema = pform.Fieldset(

    pform.PasswordField(
        'password',
        title=const.PASSWORD_TITLE,
        description=const.PASSWORD_DESCR,
        validator=passwordValidator)
    )
