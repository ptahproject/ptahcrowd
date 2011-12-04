""" schemas """
from pyramid.compat import string_types

import ptah
from ptah import form
from ptah.password import passwordValidator

from ptah_crowd.settings import _


def lower(s):
    if isinstance(s, string_types):
        return s.lower()
    return s


def checkLoginValidator(node, login):
    if getattr(node, 'value', None) == login:
        return

    if ptah.auth_service.get_principal_bylogin(login) is not None:
        raise form.Invalid(node, _('Login already is in use.'))


RegistrationSchema = form.Fieldset(

    form.TextField(
        'name',
        title=_('Full Name'),
        description=_("e.g. John Smith. This is how users "
                      "on the site will identify you."),
        ),

    form.TextField(
        'login',
        title = _('E-mail/Login'),
        description = _('This is the username you will use to log in. '
                        'It must be an email address. <br /> Your email address '
                        'will not be displayed to any user or be shared with '
                        'anyone else.'),
        preparer = lower,
        validator = form.All(form.Email(), checkLoginValidator),
        )
    )


ResetPasswordSchema = form.Fieldset(

    form.TextField(
        'login',
        title = _('Login Name'),
        description = _('Login names are not case sensitive.'),
        missing = '',
        default = '')
    )


UserSchema = form.Fieldset(

    form.fields.TextField(
        'name',
        title=_('Full Name'),
        description=_("e.g. John Smith. This is how users "
                      "on the site will identify you."),
        ),

    form.fields.TextField(
        'login',
        title = _('E-mail/Login'),
        description=_('This is the username you will use to log in. '
                      'It must be an email address. <br /> Your email address '
                      'will not be displayed to any user or be shared with '
                      'anyone else.'),
        preparer = lower,
        validator = form.All(form.Email(), checkLoginValidator),
        ),

    form.fields.TextField(
        'password',
        title = _('Password'),
        description = _('Enter password. '\
                        'No spaces or special characters, should contain '\
                        'digits and letters in mixed case.'),
        validator = passwordValidator),

    form.fields.BoolField(
        'validated',
        title = _('Validated'),
        default = True,
        ),

    form.fields.BoolField(
        'suspended',
        title = _('Suspended'),
        default = False,
        ),

    )


ManagerChangePasswordSchema = form.Fieldset(

    form.PasswordField(
        'password',
        title = _('New password'),
        description = _('Enter new password. '\
                        'No spaces or special characters, should contain '\
                        'digits and letters in mixed case.'),
        validator = passwordValidator)
    )
