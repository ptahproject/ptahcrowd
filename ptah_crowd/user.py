""" add/edit user """
from zope import interface
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import form
from ptah.password import passwordValidator

import ptah_crowd
from ptah_crowd.settings import _
from ptah_crowd.module import CrowdModule
from ptah_crowd.provider import UserSecurity
from ptah_crowd.provider import CrowdUser, CrowdGroup, CrowdFactory
from ptah_crowd.schemas import UserSchema, ManagerChangePasswordSchema


def get_roles_vocabulary(context):
    roles = []
    for name, role in ptah.get_roles().items():
        if role.system:
            continue

        roles.append([role.title,
                      form.SimpleTerm(role.id, role.id, role.title)])

    return form.SimpleVocabulary(*[term for _t, term in sorted(roles)])


def get_groups_vocabulary(context):
    groups = []
    for grp in ptah.get_session().query(CrowdGroup).all():
        groups.append(
            (grp.title,
             form.SimpleTerm(grp.__uri__, grp.__uri__, grp.title)))

    groups.sort()
    return form.SimpleVocabulary(*[term for _t, term in sorted(groups)])


@view_config('create.html',
             context=CrowdModule,
             wrapper=ptah.wrap_layout())

class CreateUserForm(form.Form):

    csrf = True
    label = _('Create new user')
    fields = UserSchema

    @form.button(_('Back'))
    def back(self):
        return HTTPFound(location='.')

    @form.button(_('Create'), actype=form.AC_PRIMARY)
    def create(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        # create user
        cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD, self.request.registry)
        tp = cfg['type']
        if not tp.startswith('cms-type:'):
            tp = 'cms-type:{0}'.format(tp)

        tinfo = ptah.resolve(tp)

        user = tinfo.create(
            title=data['name'], login=data['login'], email=data['login'])
        user.password = ptah.pwd_tool.encode(data['password'])

        crowd = CrowdFactory()
        crowd.add(user)

        # notify system
        self.request.registry.notify(ptah.events.PrincipalAddedEvent(user))

        # set props
        props = ptah_crowd.get_properties(user.__uri__)
        props.validated = data['validated']
        props.suspended = data['suspended']

        self.message('User has been created.', 'success')
        return HTTPFound(location='.')


@view_config(context=CrowdUser,
             wrapper=ptah.wrap_layout(),
             route_name=ptah_crowd.CROWD_APP_ID)

class ModifyUserForm(form.Form):

    csrf = True
    label = 'Update user'
    fields = form.Fieldset(
        UserSchema['name'],
        UserSchema['login'],
        form.fields.TextField(
            'password',
            title = _('Password'),
            description = _('Enter password. '\
                            'No spaces or special characters, should contain '\
                            'digits and letters in mixed case.'),
            missing = ptah.form.null,
            validator = passwordValidator),
        UserSchema['validated'],
        UserSchema['suspended'],

        form.fields.MultiChoiceField(
            'roles',
            title = _('Roles'),
            description = _('Choose user default roles.'),
            missing = (),
            required = False,
            voc_factory = get_roles_vocabulary),

        form.fields.MultiChoiceField(
            'groups',
            title = _('Groups'),
            description = _('Choose user groups.'),
            missing = (),
            required = False,
            voc_factory = get_groups_vocabulary)
        )

    def form_content(self):
        user = self.context
        props = ptah_crowd.get_properties(user.__uri__)

        sdata = ptah.get_session().query(UserSecurity).filter(
                      UserSecurity.user == user.__uri__).all()

        roles = [r.value for r in sdata if r.type == 0]
        groups = [r.value for r in sdata if r.type == 1]

        return {'name': user.name,
                'login': user.login,
                'password': '',
                'validated': props.validated,
                'suspended': props.suspended,
                'roles': roles,
                'groups': groups}

    @form.button(_('Modify'), actype=form.AC_PRIMARY)
    def modify(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        user = self.context

        # update attrs
        user.title = data['name']
        user.login = data['login']
        user.email = data['login']
        if data['password'] is not ptah.form.null:
            user.password = ptah.pwd_tool.encode(data['password'])

        # update props
        props = ptah_crowd.get_properties(user.__uri__)
        props.validated = data['validated']
        props.suspended = data['suspended']

        # remove user security mapping
        session = ptah.get_session()
        session.query(UserSecurity).filter(
            UserSecurity.user == user.__uri__).delete()

        # add roles info
        for role in data['roles']:
            session.add(UserSecurity(user=user.__uri__, type=0, value=role))

        # add groups info
        for grp in data['groups']:
            session.add(UserSecurity(user=user.__uri__, type=1, value=grp))

        self.message("User properties has been updated.", 'info')

    @form.button(_('Remove'), actype=form.AC_DANGER)
    def remove(self):
        self.validate_csrf_token()

        user = self.context
        Session = ptah.get_session()
        Session.delete(user)
        Session.flush()

        self.message("User has been removed.", 'info')
        return HTTPFound(location='..')

    @form.button(_('Change password'), name='changepwd')
    def password(self):
        return HTTPFound(location='password.html')

    @form.button(_('Back'))
    def back(self):
        return HTTPFound(location='..')


@view_config('password.html',
             context=CrowdUser,
             wrapper=ptah.wrap_layout(),
             route_name=ptah_crowd.CROWD_APP_ID)

class ChangePasswordForm(form.Form):

    csrf = True
    fields = form.Fieldset(ManagerChangePasswordSchema)

    label = _('Change password')
    description = _('Please specify password for this users.')

    @form.button(_('Back'))
    def back(self):
        return HTTPFound(location='..')

    @form.button(_('Change'), actype=form.AC_PRIMARY)
    def change(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        sm = self.request.registry

        self.context.password = ptah.pwd_tool.encode(data['password'])

        self.message("User password has been changed.")
