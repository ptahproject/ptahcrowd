""" add/edit user """
import pform
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah.password import passwordValidator

import ptahcrowd
from ptahcrowd import const
from ptahcrowd.settings import _
from ptahcrowd.module import CrowdModule
from ptahcrowd.provider import CrowdUser, CrowdGroup
from ptahcrowd.schemas import UserSchema


def get_roles_vocabulary(context):
    roles = []
    for name, role in ptah.get_roles().items():
        if role.system:
            continue

        roles.append([role.title,
                      pform.SimpleTerm(role.id, role.id, role.title)])

    return pform.SimpleVocabulary(*[term for _t, term in sorted(roles)])


def get_groups_vocabulary(context):
    groups = []
    for grp in ptah.get_session().query(CrowdGroup).all():
        groups.append(
            (grp.title,
             pform.SimpleTerm(grp.__uri__, grp.__uri__, grp.title)))

    groups.sort()
    return pform.SimpleVocabulary(*[term for _t, term in sorted(groups)])


@view_config(name='create.html',
             context=CrowdModule,
             wrapper=ptah.wrap_layout())
class CreateUserForm(pform.Form):

    csrf = True
    label = _('Create new user')
    fields = UserSchema

    @pform.button(_('Back'))
    def back(self):
        return HTTPFound(location='.')

    @pform.button(_('Create'), actype=pform.AC_PRIMARY)
    def create(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        # create user
        cfg = ptah.get_settings(ptahcrowd.CFG_ID_CROWD, self.request.registry)
        tp = cfg['type']
        if not tp.startswith('type:'):
            tp = 'type:{0}'.format(tp)

        tinfo = ptah.resolve(tp)

        user = tinfo.create(
            name=data['name'], login=data['login'], email=data['login'],
            validated=data['validated'], suspended=data['suspended'])
        user.password = ptah.pwd_tool.encode(data['password'])

        tinfo.add(user)

        # notify system
        self.request.registry.notify(ptah.events.PrincipalAddedEvent(user))

        self.request.add_message('User has been created.', 'success')
        return HTTPFound(location='.')


@view_config(context=CrowdUser,
             wrapper=ptah.wrap_layout(),
             route_name=ptahcrowd.CROWD_APP_ID)
class ModifyUserForm(pform.Form):

    csrf = True
    label = 'Update user'
    fields = pform.Fieldset(
        UserSchema['name'],
        UserSchema['login'],
        pform.fields.TextField(
            'password',
            title=const.PASSWORD_TITLE,
            description=const.PASSWORD_DESCR,
            missing=pform.null,
            validator=passwordValidator),
        UserSchema['validated'],
        UserSchema['suspended'],

        pform.fields.MultiChoiceField(
            'roles',
            title=_('Roles'),
            description=_("Choose user default roles."),
            missing=(),
            required=False,
            voc_factory=get_roles_vocabulary),

        pform.fields.MultiChoiceField(
            'groups',
            title=_("Groups"),
            description=_("Choose user groups."),
            missing=(),
            required=False,
            voc_factory=get_groups_vocabulary)
        )

    def form_content(self):
        user = self.context

        return {'name': user.name,
                'login': user.login,
                'password': '',
                'validated': user.validated,
                'suspended': user.suspended,
                'roles': user.properties.get('roles', ()),
                'groups': user.properties.get('groups', ())}

    @pform.button(_('Modify'), actype=pform.AC_PRIMARY)
    def modify(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        user = self.context

        # update attrs
        user.name = data['name']
        user.login = data['login']
        user.email = data['login']
        user.validated = data['validated']
        user.suspended = data['suspended']
        user.properties['roles'] = data['roles']
        user.properties['groups'] = data['groups']

        if data['password'] is not pform.null:
            user.password = ptah.pwd_tool.encode(data['password'])

        self.request.add_message(_("User properties have been updated."), 'info')

    @pform.button(_('Remove'), actype=pform.AC_DANGER)
    def remove(self):
        self.validate_csrf_token()

        user = self.context
        Session = ptah.get_session()
        Session.delete(user)
        Session.flush()

        self.request.add_message(_("User has been removed."), 'info')
        return HTTPFound(location='..')

    @pform.button(_('Back'))
    def back(self):
        return HTTPFound(location='..')
