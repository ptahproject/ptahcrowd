import sqlalchemy as sqla
from pyramid.config import Configurator
from pyramid.events import ApplicationCreated

import ptah
from ptah.password import ID_PASSWORD_CHANGER
from ptah_crowd.settings import CFG_ID_CROWD
from ptah_crowd.memberprops import get_properties

CROWD_APP_ID = 'ptah-crowd'


class CrowdUser(ptah.cms.BaseContent):

    __tablename__ = 'ptah_crowd'

    __type__ = ptah.cms.Type(
        'ptah-crowd-user', 'Crowd user', global_allow = False)

    login = sqla.Column(sqla.Unicode(255), unique=True)
    email = sqla.Column(sqla.Unicode(255), unique=True)
    password = sqla.Column(sqla.Unicode(255))

    @property
    def name(self):
        return self.title

    @property
    def properties(self):
        return get_properties(self.__uri__)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s<%s:%s>'%(self.__class__.__name__, self.title, self.__uri__)


def get_allowed_content_types(context, registry=None):
    CROWD = ptah.get_settings(CFG_ID_CROWD, registry)
    return (CROWD['type'],)


class CrowdApplication(ptah.cms.BaseApplicationRoot,ptah.cms.BaseContainer):

    __type__ = ptah.cms.Type('ptah-crowd-provider',
                             'Ptah user management',
                             filter_content_types = True,
                             allowed_content_types = get_allowed_content_types)

    def add(self, user):
        Session = ptah.get_session()
        Session.add(user)
        Session.flush()

        self[str(user.__id__)] = user


@ptah.auth_provider('ptah-crowd-auth')
class CrowdAuthProvider(object):

    _sql_get_login = ptah.QueryFreezer(
        lambda: ptah.get_session().query(CrowdUser)\
            .filter(CrowdUser.login==sqla.sql.bindparam('login')))

    _sql_search = ptah.QueryFreezer(
        lambda: ptah.get_session().query(CrowdUser) \
            .filter(sqla.sql.or_(
                CrowdUser.email.contains(sqla.sql.bindparam('term')),
                CrowdUser.title.contains(sqla.sql.bindparam('term'))))\
            .order_by(sqla.sql.asc('title')))

    def authenticate(self, creds):
        login, password = creds['login'], creds['password']

        user = self._sql_get_login.first(login=login)
        if user is not None:
            if ptah.pwd_tool.check(user.password, password):
                return user

    def get_principal_bylogin(self, login):
        return self._sql_get_login.first(login=login)

    @classmethod
    def search(cls, term):
        for user in cls._sql_search.all(term = '%%%s%%'%term):
            yield user

    @staticmethod
    def change_password(principal, password):
        principal.password = password


CrowdFactory = ptah.cms.ApplicationFactory(
    CrowdApplication,
    name = CROWD_APP_ID,
    title = 'Ptah user management')


@ptah.subscriber(ApplicationCreated)
def initialize(ev):
    cfg = Configurator(ev.app.registry, autocommit=True)

    settings = ptah.get_settings(CFG_ID_CROWD, ev.app.registry)

    tp = settings['type']
    if not tp.startswith('cms-type:'):
        tp = 'cms-type:{0}'.format(tp)

    tinfo = ptah.resolve(tp)
    if tinfo is not None:
        if tinfo.schema not in ptah.get_cfg_storage(ID_PASSWORD_CHANGER):
            cfg.ptah_password_changer(
                tinfo.schema, CrowdAuthProvider.change_password)
            cfg.ptah_principal_searcher(
                tinfo.schema, CrowdAuthProvider.search)
