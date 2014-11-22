import ptah
import ptah.form
import translationstring

_ = translationstring.TranslationStringFactory('ptahcrowd')

CFG_ID_AUTH = 'auth'
CFG_ID_CROWD = 'ptahcrowd'

providers = ptah.form.Vocabulary(
    ptah.form.Term('bitbucket', 'bitbucket', 'Bitbucket'),
    ptah.form.Term('facebook', 'facebook', 'Facebook'),
    ptah.form.Term('github', 'github', 'GitHub'),
    ptah.form.Term('google', 'google', 'Google'),
    ptah.form.Term('linkedin', 'linkedin', 'LinkedIn'),
    ptah.form.Term('live', 'live', 'Windows Live'),
    ptah.form.Term('twitter', 'twitter', 'Twitter'),
    )


ptah.register_settings(
    CFG_ID_CROWD,

    ptah.form.TextField(
        'type',
        title = 'User content type',
        description = 'User content type for crowd user provider.',
        default = 'ptah-crowd-user'),

    ptah.form.BoolField(
        'join',
        title = 'Site registration',
        description = 'Enable/Disable site registration.',
        default = True),

    ptah.form.TextField(
        'join-url',
        title = 'Join url',
        description = 'Custom join form url.',
        default = '/join.html'),

    ptah.form.TextField(
        'login-url',
        title = 'Login url',
        description = 'Custom login form url.',
        default = '/login.html'),

    ptah.form.TextField(
        'success-url',
        title = 'Successfull login url',
        description = 'Successfull logig redirect url.',
        default = ''),

    ptah.form.BoolField(
        'password',
        title = 'User password',
        description = 'Allow user to select password during registration.',
        default = False),

    ptah.form.BoolField(
        'validation',
        title = 'Email validation',
        description = 'Validate user account by email.',
        default = True),

    ptah.form.BoolField(
        'allow-unvalidated',
        title = 'Allow unvalidated',
        description = 'Allow login for unvalidated users.',
        default = True),

    ptah.form.TextField(
        'admin-name',
        title = 'Admin name',
        description = 'Default admin name.',
        default = 'Ptah admin'),

    ptah.form.TextField(
        'admin-login',
        title = 'Admin login',
        description = 'Default admin login.',
        default = ''),

    ptah.form.TextField(
        'admin-password',
        title = 'Admin password',
        description = 'Default admin password.',
        default = '12345',
        tint = True),

    ptah.form.TextField(
        'admin-role',
        title = 'Admin role',
        description = 'Default admin role.',
        default = ''),

    title = 'Ptah crowd settings',
    )


ptah.register_settings(
    CFG_ID_AUTH,

    ptah.form.LinesField(
        'providers',
        title = 'Providers',
        description = 'Enable external auth providers (github, facebook, etc).',
        default = ()),

    ptah.form.TextField(
        'github_id',
        title = 'Client id',
        description = 'Github client id.',
        default = ''),

    ptah.form.TextField(
        'github_secret',
        title = 'Secret',
        description = 'Github client secret.',
        default = '',
        tint = True),

    ptah.form.TextField(
        'github_scope',
        title = 'Scope',
        description = 'Github access oauth scope.',
        default = ''),

    ptah.form.TextField(
        'facebook_id',
        title = 'Id',
        description = 'Facebook client id.',
        default = ''),

    ptah.form.TextField(
        'facebook_secret',
        title = 'Secret',
        description = 'Facebook client secret.',
        default = '',
        tint = True),

    ptah.form.TextField(
        'facebook_scope',
        title = 'Scope',
        description = 'Facebook access oauth scope.',
        default = 'email'),

    ptah.form.TextField(
        'google_id',
        title = 'Id',
        description = 'Google client id.',
        default = ''),

    ptah.form.TextField(
        'google_secret',
        title = 'Secret',
        description = 'Google client secret.',
        default = '',
        tint = True),

    ptah.form.TextField(
        'live_id',
        title = 'Id',
        description = 'Windows Live client id.',
        default = ''),

    ptah.form.TextField(
        'live_secret',
        title = 'Secret',
        description = 'Windows Live client secret.',
        default = '',
        tint = True),

    ptah.form.TextField(
        'twitter_key',
        title = 'Key',
        description = 'Twitter consumer key.',
        default = ''),

    ptah.form.TextField(
        'twitter_secret',
        title = 'Secret',
        description = 'Twitter consumer secret.',
        default = '',
        tint = True),

    title = 'Ptah external auth providers',
)
