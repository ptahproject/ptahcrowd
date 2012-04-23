""" schemas """
from pyramid.compat import string_types

import ptah
from ptah import form
from ptah.password import passwordValidator

from ptah_crowd import const
from ptah_crowd.settings import _


def lower(s):
    if isinstance(s, string_types):
        return s.lower()
    return s


def checkLoginValidator(field, login):
    """Ptah field validator, checks if login is already in use."""

    if getattr(field, 'value', None) == login:
        return

    if ptah.auth_service.get_principal_bylogin(login) is not None:
        raise form.Invalid(field, _("This login is already in use."))


RegistrationSchema = form.Fieldset(

    form.TextField(
        'name',
        title=const.NAME_TITLE,
        description=const.NAME_DESCR,
        ),

    form.TextField(
        'login',
        title=const.LOGIN_TITLE,
        description=const.LOGIN_DESCR,
        preparer=lower,
        validator=form.All(form.Email(), checkLoginValidator),
        )
    )


ResetPasswordSchema = form.Fieldset(

    form.TextField(
        'login',
        title=const.LOGIN_TITLE,
        description=const.CASE_DESCR,
        missing='',
        default='')
    )


UserSchema = form.Fieldset(

    form.fields.TextField(
        'name',
        title=const.NAME_TITLE,
        description=const.NAME_DESCR,
        ),

    form.fields.TextField(
        'login',
        title=const.LOGIN_TITLE,
        description=const.LOGIN_DESCR,
        preparer=lower,
        validator=form.All(form.Email(), checkLoginValidator),
        ),

    form.fields.TextField(
        'password',
        title=const.PASSWORD_TITLE,
        description=const.PASSWORD_DESCR,
        validator=passwordValidator),

    form.fields.BoolField(
        'validated',
        title=_('Validated'),
        default=True,
        ),

    form.fields.BoolField(
        'suspended',
        title=_('Suspended'),
        default=False,
        ),

    )


ManagerChangePasswordSchema = form.Fieldset(

    form.PasswordField(
        'password',
        title=const.PASSWORD_TITLE,
        description=const.PASSWORD_DESCR,
        validator=passwordValidator)
    )
