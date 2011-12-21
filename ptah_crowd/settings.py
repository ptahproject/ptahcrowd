import ptah
import translationstring

_ = translationstring.TranslationStringFactory('ptah_crowd')


CFG_ID_CROWD = 'ptah-crowd'

ptah.register_settings(
    CFG_ID_CROWD,

    ptah.form.TextField(
        'type',
        title = 'User content type',
        description = 'User content type for crowd user provider',
        default = 'ptah-crowd-user'),

    ptah.form.BoolField(
        'join',
        title = 'Site registration',
        description = 'Enable/Disable site registration',
        default = True),

    ptah.form.TextField(
        'joinurl',
        title = 'Join form url',
        default = ''),

    ptah.form.BoolField(
        'password',
        title = 'User password',
        description = 'Allow use to select password during registration',
        default = False),

    ptah.form.BoolField(
        'validation',
        title = 'Email validation',
        description = 'Validate user account by email.',
        default = True),

    ptah.form.BoolField(
        'allow-unvalidated',
        title = 'Allow un validation',
        description = 'Allow login for un Validated users.',
        default = True),

    title = 'Ptah crowd settings',
    #ttw = True,
    #ttw_skip_fields = ('type',),
    )
