import ptah
import pform
import translationstring

_ = translationstring.TranslationStringFactory('ptahcrowd')

CFG_ID_AUTH = 'auth'
CFG_ID_CROWD = 'ptahcrowd'

providers = pform.SimpleVocabulary(
    pform.SimpleTerm('bitbucket', 'bitbucket', 'Bitbucket'),
    pform.SimpleTerm('facebook', 'facebook', 'Facebook'),
    pform.SimpleTerm('github', 'github', 'GitHub'),
    pform.SimpleTerm('google', 'google', 'Google'),
    pform.SimpleTerm('linkedin', 'linkedin', 'LinkedIn'),
    pform.SimpleTerm('live', 'live', 'Windows Live'),
    pform.SimpleTerm('twitter', 'twitter', 'Twitter'),
    )


ptah.register_settings(
    CFG_ID_CROWD,

    pform.TextField(
        'type',
        title = 'User content type',
        description = 'User content type for crowd user provider.',
        default = 'ptah-crowd-user'),

    pform.BoolField(
        'join',
        title = 'Site registration',
        description = 'Enable/Disable site registration.',
        default = True),

    pform.TextField(
        'join-url',
        title = 'Join url',
        description = 'Custom join form url.',
        default = ''),

    pform.TextField(
        'login-url',
        title = 'Login url',
        description = 'Custom login form url.',
        default = ''),

    pform.TextField(
        'success-url',
        title = 'Successfull login url',
        description = 'Successfull logig redirect url.',
        default = ''),

    pform.BoolField(
        'password',
        title = 'User password',
        description = 'Allow user to select password during registration.',
        default = False),

    pform.BoolField(
        'validation',
        title = 'Email validation',
        description = 'Validate user account by email.',
        default = True),

    pform.BoolField(
        'allow-unvalidated',
        title = 'Allow unvalidated',
        description = 'Allow login for unvalidated users.',
        default = True),

    pform.TextField(
        'admin-name',
        title = 'Admin name',
        description = 'Default admin name.',
        default = 'Ptah admin'),

    pform.TextField(
        'admin-login',
        title = 'Admin login',
        description = 'Default admin login.',
        default = ''),

    pform.TextField(
        'admin-password',
        title = 'Admin password',
        description = 'Default admin password.',
        default = '12345',
        tint = True),

    pform.TextField(
        'admin-role',
        title = 'Admin role',
        description = 'Default admin role.',
        default = ''),

    title = 'Ptah crowd settings',
    )


ptah.register_settings(
    CFG_ID_AUTH,

    pform.LinesField(
        'providers',
        title = 'Providers',
        description = 'Enable external auth providers (github, facebook, etc).',
        default = ()),

    pform.TextField(
        'github_id',
        title = 'Client id',
        description = 'Github client id.',
        default = ''),

    pform.TextField(
        'github_secret',
        title = 'Secret',
        description = 'Github client secret.',
        default = '',
        tint = True),

    pform.TextField(
        'github_scope',
        title = 'Scope',
        description = 'Github access oauth scope.',
        default = ''),

    pform.TextField(
        'facebook_id',
        title = 'Id',
        description = 'Facebook client id.',
        default = ''),

    pform.TextField(
        'facebook_secret',
        title = 'Secret',
        description = 'Facebook client secret.',
        default = '',
        tint = True),

    pform.TextField(
        'facebook_scope',
        title = 'Scope',
        description = 'Facebook access oauth scope.',
        default = 'email'),

    pform.TextField(
        'google_id',
        title = 'Id',
        description = 'Google client id.',
        default = ''),

    pform.TextField(
        'google_secret',
        title = 'Secret',
        description = 'Google client secret.',
        default = '',
        tint = True),

    pform.TextField(
        'live_id',
        title = 'Id',
        description = 'Windows Live client id.',
        default = ''),

    pform.TextField(
        'live_secret',
        title = 'Secret',
        description = 'Windows Live client secret.',
        default = '',
        tint = True),

    pform.TextField(
        'twitter_key',
        title = 'Key',
        description = 'Twitter consumer key.',
        default = ''),

    pform.TextField(
        'twitter_secret',
        title = 'Secret',
        description = 'Twitter consumer secret.',
        default = '',
        tint = True),

    title = 'Ptah external auth providers',
)
