import sqlalchemy as sqla
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptah
import ptah_crowd
from ptah import form
from ptah_crowd.settings import _
from ptah_crowd.module import CrowdModule
from ptah_crowd.provider import CrowdUser, CrowdGroup, CrowdFactory
from ptah_crowd.providers import Storage
from ptah_crowd.memberprops import UserProperties


@view_config(
    context=CrowdModule,
    wrapper=ptah.wrap_layout(),
    renderer='ptah_crowd:templates/users.pt')

class CrowdApplicationView(form.Form):
    __doc__ = 'List/search users view'

    csrf = True
    fields = form.Fieldset(
        form.TextField(
            'term',
            title = _('Search term'),
            description = _('Ptah searches users by login and email'),
            missing = '',
            default = '')
        )

    users = None
    external = {}
    pages = ()
    page = ptah.Pagination(15)

    def form_content(self):
        return {'term': self.request.session.get('ptah-search-term', '')}

    def update(self):
        super(CrowdApplicationView, self).update()

        request = self.request
        self.manage_url = ptah.manage.get_manage_url(self.request)

        Session = ptah.get_session()
        uids = request.POST.getall('uid')

        if 'activate' in request.POST and uids:
            Session.query(UserProperties)\
                .filter(UserProperties.uri.in_(uids))\
                .update({'suspended': False}, False)
            self.message("Selected accounts have been activated.", 'info')

        if 'suspend' in request.POST and uids:
            Session.query(UserProperties).filter(
                UserProperties.uri.in_(uids))\
                .update({'suspended': True}, False)
            self.message("Selected accounts have been suspended.", 'info')

        if 'validate' in request.POST and uids:
            Session.query(UserProperties).filter(
                UserProperties.uri.in_(uids))\
                .update({'validated': True}, False)
            self.message("Selected accounts have been validated.", 'info')

        if 'remove' in request.POST and uids:
            crowd = CrowdFactory()
            for user in Session.query(CrowdUser).filter(
                CrowdUser.__uri__.in_(uids)):
                Session.delete(ptah_crowd.get_properties(user.__uri__))
                del crowd[user.__name__]
            self.message("Selected accounts have been removed.", 'info')

        term = request.session.get('ptah-search-term', '')
        if term:
            self.users = Session.query(CrowdUser) \
                .filter(sqla.sql.or_(
                    CrowdUser.email.contains('%%%s%%'%term),
                    CrowdUser.title.contains('%%%s%%'%term)))\
                .order_by(sqla.sql.asc('name')).all()
        else:
            self.size = Session.query(CrowdUser).count()

            try:
                current = int(request.params.get('batch', None))
                if not current:
                    current = 1

                request.session['crowd-current-batch'] = current
            except:
                current = request.session.get('crowd-current-batch')
                if not current:
                    current = 1

            self.current = current

            self.pages, self.prev, self.next = self.page(self.size,self.current)

            offset, limit = self.page.offset(current)
            self.users = Session.query(CrowdUser)\
                    .offset(offset).limit(limit).all()

            auths = Session.query(Storage).filter(
                Storage.uri.in_([u.__uri__ for u in self.users])).all()

            self.external = extr = {}
            for entry in auths:
                data = extr.get(entry.uri)
                if data is None:
                    data = []
                data.append(entry.domain)
                extr[entry.uri] = data

    @form.button(_('Search'), actype=form.AC_PRIMARY)
    def search(self):
        data, error = self.extract()

        if not data['term']:
            self.message('Please specify search term', 'warning')
            return

        self.request.session['ptah-search-term'] = data['term']

    @form.button(_('Clear term'), name='clear')
    def clear(self):
        if 'ptah-search-term' in self.request.session:
            del self.request.session['ptah-search-term']


@view_config(
    'groups.html',
    context=CrowdModule,
    wrapper=ptah.wrap_layout(),
    renderer='ptah_crowd:templates/groups.pt')

class CrowdGroupsView(ptah.View):
    __doc__ = 'List groups view'

    pages = ()
    page = ptah.Pagination(15)

    def update(self):
        request = self.request
        self.manage_url = ptah.manage.get_manage_url(request)

        Session = ptah.get_session()
        uids = request.POST.getall('uid')

        if 'remove' in request.POST and uids:
            crowd = CrowdFactory()
            for grp in Session.query(CrowdGroup).\
                    filter(CrowdGroup.__uri__.in_(uids)):
                del crowd[grp.__name__]
            self.message("Selected groups have been removed.", 'info')

        self.size = Session.query(CrowdGroup).count()

        try:
            current = int(request.params.get('batch', None))
            if not current:
                current = 1

            request.session['crowd-grp-batch'] = current
        except:
            current = request.session.get('crowd-grp-batch')
            if not current:
                current = 1

        self.current = current
        self.pages, self.prev, self.next = self.page(self.size, self.current)

        offset, limit = self.page.offset(current)
        self.groups = Session.query(CrowdGroup)\
                      .offset(offset).limit(limit).all()


@view_config('create-grp.html',
             context=CrowdModule,
             wrapper=ptah.wrap_layout())

class CreateGroupForm(form.Form):

    csrf = True
    label = _('Create new group')
    fields = ptah.cms.ContentSchema

    @form.button(_('Back'))
    def back(self):
        return HTTPFound(location='groups.html')

    @form.button(_('Create'), actype=form.AC_PRIMARY)
    def create(self):
        data, errors = self.extract()

        if errors:
            self.message(errors, 'form-error')
            return

        # create grp
        grp = CrowdGroup.__type__.create(
            title=data['title'], description=data['description'])
        crowd = CrowdFactory()
        crowd.add(grp)

        self.message('Group has been created.', 'success')
        return HTTPFound(location='groups.html')
