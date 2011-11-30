import ptah
import sqlalchemy as sqla


class CrowdUser(ptah.cms.BaseContent):

    __tablename__ = 'ptah_crowd_users'

    __type__ = ptah.cms.Type('ptah-crowd-user', 'Crowd user',
                             global_allow = False)

    login = sqla.Column(sqla.Unicode(255), unique=True)
    email = sqla.Column(sqla.Unicode(255), unique=True)
    password = sqla.Column(sqla.Unicode(255))

    @property
    def name(self):
        return self.__name__


class CrowdAuthApplication(ptah.cms.BaseApplicationRoot,ptah.cms.BaseContainer):

    __type__ = ptah.cms.Type('ptah-crowd-provider',
                             'Ptah user management',
                             filter_content_types = True,
                             allowed_content_types = ('ptah-crowd-user',))


class CrowdAuthProvider(object):
    ptah.auth_provider('ptah-crowd-auth')

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
