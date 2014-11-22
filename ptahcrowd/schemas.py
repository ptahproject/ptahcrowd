""" schemas """
import ptah.form
from pyramid.compat import string_types

import ptah
from ptah.password import passwordValidator

import ptahcrowd
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

    session = ptah.get_session()
    user = session.query(ptahcrowd.CrowdUser).filter(
        ptahcrowd.CrowdUser.username == username).first()

    if user is not None:
        raise ptah.form.Invalid(_("This login is already in use."), field)

def checkEmailValidator(field, email):
    """Ptah field validator, checks if email is already in use."""

    if getattr(field, 'value', None) == email:
        return

    session = ptah.get_session()
    user = session.query(ptahcrowd.CrowdUser).filter(
        ptahcrowd.CrowdUser.email == email).first()

    if user is not None:
        raise ptah.form.Invalid(_("This email is already in use."), field)


RegistrationSchema = ptah.form.Fieldset(

    ptah.form.TextField(
        'username',
        title=const.USERNAME_TITLE,
        description=const.USERNAME_DESCR,
        validator=checkUsernameValidator,
        ),

    ptah.form.TextField(
        'email',
        title=const.EMAIL_TITLE,
        description=const.EMAIL_DESCR,
        preparer=lower,
        validator=ptah.form.All(ptah.form.Email(), checkEmailValidator),
        )
    )


ResetPasswordSchema = ptah.form.Fieldset(

    ptah.form.TextField(
        'login',
        title=const.LOGIN_TITLE,
        description=' '.join([const.LOGIN_DESCR, const.CASE_DESCR]),
        missing='',
        default='')
    )


UserSchema = ptah.form.Fieldset(

    ptah.form.fields.TextField(
        'fullname',
        title=const.FULLNAME_TITLE,
        description=const.FULLNAME_DESCR,
        required=False
        ),

    ptah.form.fields.TextField(
        'username',
        title=const.USERNAME_TITLE,
        description=const.USERNAME_DESCR,
        validator=checkUsernameValidator,
        ),

    ptah.form.fields.TextField(
        'email',
        title=const.EMAIL_TITLE,
        description=const.EMAIL_DESCR,
        preparer=lower,
        validator=ptah.form.All(ptah.form.Email(), checkEmailValidator),
        ),

    ptah.form.fields.TextField(
        'password',
        title=const.PASSWORD_TITLE,
        description=const.PASSWORD_DESCR,
        validator=passwordValidator),

    ptah.form.fields.BoolField(
        'validated',
        title=_('Validated'),
        default=True,
        ),

    ptah.form.fields.BoolField(
        'suspended',
        title=_('Suspended'),
        default=False,
        ),

    )


ManagerChangePasswordSchema = ptah.form.Fieldset(

    ptah.form.PasswordField(
        'password',
        title=const.PASSWORD_TITLE,
        description=const.PASSWORD_DESCR,
        validator=passwordValidator)
    )
