import sqlalchemy as sqla
import pform
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from player import renderer

import ptah
import ptahcrowd
from ptahcrowd.settings import _
from ptahcrowd.module import CrowdModule
from ptahcrowd.provider import CrowdUser, CrowdGroup
from ptahcrowd.providers import Storage


@view_config(
    context=CrowdModule,
    wrapper=ptah.wrap_layout(), renderer='ptah-crowd:users.lt')
class CrowdModuleView(pform.Form, ptah.View):
    __doc__ = 'List/search users view'

    csrf = True
    fields = pform.Fieldset(
        pform.TextField(
            'term',
            title=_('Search term'),
            description=_('Ptah searches users by login and email'),
            missing='',
            default='')
        )

    users = None
    external = {}
    pages = ()
    page = ptah.Pagination(15)

    def form_content(self):
        return {'term': self.request.session.get('ptah-search-term', '')}

    def update(self):
        super(CrowdModuleView, self).update()

        request = self.request
        self.manage_url = ptah.manage.get_manage_url(self.request)

        Session = ptah.get_session()
        uids = request.POST.getall('uid')

        if 'create' in request.POST:
            return HTTPFound('create.html')

        if 'activate' in request.POST and uids:
            Session.query(CrowdUser).filter(CrowdUser.id.in_(uids))\
                .update({'suspended': False}, False)
            self.request.add_message(
                _("The selected accounts have been activated."),'info')

        if 'suspend' in request.POST and uids:
            Session.query(CrowdUser).filter(
                CrowdUser.id.in_(uids)).update({'suspended': True}, False)
            self.request.add_message(
                _("The selected accounts have been suspended."),'info')

        if 'validate' in request.POST and uids:
            Session.query(CrowdUser).filter(CrowdUser.id.in_(uids))\
                .update({'validated': True}, False)
            self.request.add_message(
                _("The selected accounts have been validated."),'info')

        if 'remove' in request.POST and uids:
            for user in Session.query(CrowdUser).filter(CrowdUser.id.in_(uids)):
                Session.delete(user)
            self.request.add_message(
                _("The selected accounts have been removed."), 'info')

        term = request.session.get('ptah-search-term', '')
        if term:
            self.users = Session.query(CrowdUser) \
                .filter(sqla.sql.or_(
                    CrowdUser.email.contains('%%%s%%' % term),
                    CrowdUser.name.contains('%%%s%%' % term)))\
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

            self.pages, self.prev, self.next = \
                self.page(self.size, self.current)

            offset, limit = self.page.offset(current)
            self.users = Session.query(CrowdUser) \
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

    @pform.button(_('Search'), actype=pform.AC_PRIMARY)
    def search(self):
        data, error = self.extract()

        if not data['term']:
            self.request.add_message('Please specify search term', 'warning')
            return

        self.request.session['ptah-search-term'] = data['term']

    @pform.button(_('Clear term'), name='clear')
    def clear(self):
        if 'ptah-search-term' in self.request.session:
            del self.request.session['ptah-search-term']


@view_config(
    name='groups.html',
    context=CrowdModule,
    wrapper=ptah.wrap_layout(),
    renderer='ptah-crowd:groups.lt')

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
            for grp in Session.query(CrowdGroup).\
                    filter(CrowdGroup.__uri__.in_(uids)):
                grp.delete()
            self.request.add_message(
                _("The selected groups have been removed."), 'info')

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


@view_config(name='create-grp.html',
             context=CrowdModule,
             wrapper=ptah.wrap_layout())
class CreateGroupForm(pform.Form):

    csrf = True
    label = _('Create new group')

    @property
    def fields(self):
        return CrowdGroup.__type__.fieldset

    @pform.button(_('Back'))
    def back(self):
        return HTTPFound(location='groups.html')

    @pform.button(_('Create'), actype=pform.AC_PRIMARY)
    def create(self):
        data, errors = self.extract()

        if errors:
            self.add_error_message(errors)
            return

        # create grp
        grp = CrowdGroup.__type__.create(
            title=data['title'], description=data['description'])
        CrowdGroup.__type__.add(grp)

        self.request.add_message(
            _('The group has been created.'), 'success')
        return HTTPFound(location='groups.html')
