import sqlalchemy as sqla

import ptah
from ptah_crowd.settings import CROWD


class CrowdUser(ptah.cms.BaseContent):

    __tablename__ = 'ptah_crowd'

    __type__ = ptah.cms.Type('ptah-crowd', 'Crowd user',
                             global_allow = False)

    login = sqla.Column(sqla.Unicode(255), unique=True)
    email = sqla.Column(sqla.Unicode(255), unique=True)
    password = sqla.Column(sqla.Unicode(255))
    validated = sqla.Column(sqla.Boolean(), default=False)
    suspended = sqla.Column(sqla.Boolean(), default=False)
    keywords = sqla.Column('keywords', ptah.JsonDictType(), default={})

    @property
    def name(self):
        return self.title

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s<%s:%s>'%(self.__class__.__name__, self.title, self.__uri__)


def get_allowed_content_types(context):
    return (CROWD['type'],)


class CrowdAuthApplication(ptah.cms.BaseApplicationRoot,ptah.cms.BaseContainer):

    __type__ = ptah.cms.Type('ptah-crowd-provider',
                             'Ptah user management',
                             filter_content_types = True,
                             allowed_content_types = get_allowed_content_types)

    def add(self, user):
        ptah.cms.Session.add(user)
        ptah.cms.Session.flush()

        user.__name__ = str(user.__id__)


@ptah.auth_provider('ptah-crowd-auth')
class CrowdAuthProvider(object):

    _sql_get_login = ptah.QueryFreezer(
        lambda: ptah.cms.Session.query(CrowdUser)\
            .filter(CrowdUser.login==sqla.sql.bindparam('login')))

    _sql_search = ptah.QueryFreezer(
        lambda: Session.query(CrowdUser) \
            .filter(sqla.sql.or_(
                CrowdUser.email.contains(sqla.sql.bindparam('term')),
                CrowdUser.__name__.contains(sqla.sql.bindparam('term'))))\
            .order_by(sqla.sql.asc('__name__')))

    def authenticate(self, creds):
        login, password = creds['login'], creds['password']

        user = self._sql_get_login.first(login=login)
        if user is not None:
            if ptah.pwd_tool.check(user.password, password):
                return user

    def get_principal_bylogin(self, login):
        return self._sql_get_login.first(login=login)

    def search(self, term):
        for user in self._sql_search.all(term = '%%%s%%'%term):
            yield user

    def change_password(self, principal, password):
        principal.password = password


factory = ptah.cms.ApplicationFactory(
    CrowdAuthApplication, name = 'ptah-crowd', title = 'Ptah user management')
