""" add/edit user """
from zope import interface
from ptah import config, view, form
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptah
import ptah_crowd
from ptah_crowd.settings import _
from ptah_crowd.module import CrowdModule
from ptah_crowd.provider import CrowdUser, CrowdFactory
from ptah_crowd.schemas import UserSchema, ManagerChangePasswordSchema


@view_config('create.html',
             context=CrowdModule,
             wrapper=ptah.wrap_layout())

class CreateUserForm(form.Form):

    csrf = True
    label = _('Create new user')
    fields = UserSchema

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

    @form.button(_('Back'))
    def back(self):
        return HTTPFound(location='.')


@view_config(context=CrowdUser,
             wrapper=ptah.wrap_layout(),
             route_name=ptah_crowd.CROWD_APP_ID)

class ModifyUserForm(form.Form):

    csrf = True
    label = 'Update user'
    fields = form.Fieldset(UserSchema)

    def form_content(self):
        user = self.context
        props = ptah_crowd.get_properties(user.__uri__)

        return {'name': user.name,
                'login': user.login,
                'password': '',
                'validated': props.validated,
                'suspended': props.suspended}

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
        user.password = ptah.pwd_tool.encode(data['password'])

        # update props
        props = ptah_crowd.get_properties(user.__uri__)
        props.validated = data['validated']
        props.suspended = data['suspended']

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

    @form.button(_('Change'), actype=form.AC_PRIMARY)
    def change(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        sm = self.request.registry

        self.context.password = ptah.pwd_tool.encode(data['password'])

        self.message("User password has been changed.")

    @form.button(_('Back'))
    def back(self):
        return HTTPFound(location='..')
