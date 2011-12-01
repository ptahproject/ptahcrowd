import colander
import translationstring
from ptah import config

_ = translationstring.TranslationStringFactory('ptah_crowd')


CROWD_CFG_ID = 'ptah-crowd'

CROWD = config.register_settings(
    CROWD_CFG_ID,

    config.SchemaNode(
        colander.Str(),
        name = 'type',
        title = 'User content type',
        description = 'User content type for crowd user provider',
        default = ''),

    config.SchemaNode(
        colander.Bool(),
        name = 'join',
        title = 'Site registration',
        description = 'Enable/Disable site registration',
        default = True),

    config.SchemaNode(
        colander.Str(),
        name = 'joinurl',
        title = 'Join form url',
        default = ''),

    config.SchemaNode(
        colander.Bool(),
        name = 'password',
        title = 'User password',
        description = 'Allow use to select password during registration',
        default = False),

    config.SchemaNode(
        colander.Bool(),
        name = 'validation',
        title = 'Email validation',
        description = 'Validate user account by email.',
        default = True),

    config.SchemaNode(
        colander.Bool(),
        name = 'allow-unvalidated',
        title = 'Allow un validation',
        description = 'Allow login for un Validated users.',
        default = True),

    title = 'Ptah crowd settings',
    )
