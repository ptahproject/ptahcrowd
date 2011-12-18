import sqlalchemy as sqla
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound

import ptah
import ptah_crowd
from ptah import form
from ptah_crowd.settings import _
from ptah_crowd.module import CrowdModule
from ptah_crowd.provider import CrowdUser, CrowdFactory
from ptah_crowd.memberprops import MemberProperties


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
            Session.query(MemberProperties)\
                .filter(MemberProperties.uri.in_(uids))\
                .update({'suspended': False}, False)
            self.message("Selected accounts have been activated.", 'info')

        if 'suspend' in request.POST and uids:
            Session.query(MemberProperties).filter(
                MemberProperties.uri.in_(uids))\
                .update({'suspended': True}, False)
            self.message("Selected accounts have been suspended.", 'info')

        if 'validate' in request.POST and uids:
            Session.query(MemberProperties).filter(
                MemberProperties.uri.in_(uids))\
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
