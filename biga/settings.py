import colander
from ptah import config


CONFIG = config.register_settings(
    'biga',

    config.SchemaNode(
        colander.Str(),
        name = 'login',
        title = 'Login url',
        default = ''),

    title = 'biga settings',
    )
