# -*- coding: utf-8 -*-

'''Make it easy for applications to change ptah-crowd's strings by
concentrating them here. This also avoids repetition, since many of these
strings are used more than once.
'''

from ptahcrowd.settings import _


CASE_DESCR = _("This is not case sensitive.")
CASE_WARN = _("Case sensitive. Make sure the Caps Lock key is off.")
LOGIN_TITLE = _("Email")
LOGIN_DESCR = _("This is what you will use to log in. "
                "It must be an email address.<br />Your email "
                "will not be displayed to any user or be shared with "
                "anyone else.")
LOGOUT_SUCCESSFUL = _("You have been logged out.")
NAME_TITLE = _("Full name")
NAME_DESCR = _("e.g. John Smith. This is how users "
               "on the site will identify you.")
PASSWORD_TITLE = _("Password")
PASSWORD_DESCR = _("Enter your password. "
                   "No spaces or special characters; should contain "
                   "digits and letters in mixed case.")
PASSWORD_RESET_START = _("We have started resetting your password. "
                         "Please check your email for further instructions.")
PASSWORD_RESET_SUBJECT = _("Password reset confirmation")
WRONG_CREDENTIALS = _("You have entered the wrong login or password.")
