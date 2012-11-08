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


def checkLoginValidator(field, login):
    """Ptah field validator, checks if login is already in use."""

    if getattr(field, 'value', None) == login:
        return

    if ptah.auth_service.get_principal_bylogin(login) is not None:
        raise pform.Invalid(field, _("This login is already in use."))


RegistrationSchema = pform.Fieldset(

    pform.TextField(
        'name',
        title=const.NAME_TITLE,
        description=const.NAME_DESCR,
        ),

    pform.TextField(
        'login',
        title=const.LOGIN_TITLE,
        description=const.LOGIN_DESCR,
        preparer=lower,
        validator=pform.All(pform.Email(), checkLoginValidator),
        )
    )


ResetPasswordSchema = pform.Fieldset(

    pform.TextField(
        'login',
        title=const.LOGIN_TITLE,
        description=const.CASE_DESCR,
        missing='',
        default='')
    )


UserSchema = pform.Fieldset(

    pform.fields.TextField(
        'name',
        title=const.NAME_TITLE,
        description=const.NAME_DESCR,
        ),

    pform.fields.TextField(
        'login',
        title=const.LOGIN_TITLE,
        description=const.LOGIN_DESCR,
        preparer=lower,
        validator=pform.All(pform.Email(), checkLoginValidator),
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
