import sqlalchemy as sqla
from pyramid.httpexceptions import HTTPFound

import ptah
from ptah import form, view
from ptah_crowd.settings import _
from ptah_crowd.provider import factory, CrowdUser, CrowdApplication


class CrowdApplicationView(form.Form):
    view.pview(
        route = ptah.manage.MANAGE_APP_ROUTE,
        context = CrowdApplication,
        template = view.template('ptah_crowd:templates/users.pt'))

    __doc__ = 'List/search users view'
    __intr_path__ = '/ptah-manage/crowd/'

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
            Session.query(MemberProperties).filter(
                MemberProperties.uri.in_(uids)).delete()
            for user in ptah.Session.query(CrowdUser).filter(
                CrowdUser.__uri__.in_(uids)):
                del self.context[user.__name__]
            self.message("Selected accounts have been removed.", 'info')

        term = request.session.get('ptah-search-term', '')
        if term:
            self.users = ptah.Session.query(CrowdUser) \
                .filter(sqla.sql.or_(
                    CrowdUser.email.contains('%%%s%%'%term),
                    CrowdUser.title.contains('%%%s%%'%term)))\
                .order_by(sqla.sql.asc('name')).all()
        else:
            self.size = ptah.Session.query(CrowdUser).count()

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
            self.users = ptah.Session.query(CrowdUser)\
                    .offset(offset).limit(limit).all()

    @form.button(_('Search'), actype=form.AC_PRIMARY)
    def search(self):
        data, error = self.extract()

        if not data['term']:
            self.message('Please specify search term', 'warning')
            return

        self.request.session['ptah-search-term'] = data['term']
        raise HTTPFound(location = self.request.url)

    @form.button(_('Clear term'), name='clear')
    def clear(self):
        if 'ptah-search-term' in self.request.session:
            del self.request.session['ptah-search-term']
