import ptah
import sqlalchemy as sqla
import sqlahelper as sqlh

Base = sqlh.get_base()
Session = sqlh.get_session()


class CrowdProvider(object):

    def __init__(self, cls):
        self.cls = cls

        self._sql_get = ptah.QueryFreezer(
            lambda: Session.query(cls)\
                .filter(cls.pid==sqla.sql.bindparam('pid')))

        self._sql_get_uri = ptah.QueryFreezer(
            lambda: Session.query(cls)\
                .filter(cls.__uri__==sqla.sql.bindparam('uri')))

        self._sql_get_login = ptah.QueryFreezer(
            lambda: Session.query(cls)\
                .filter(cls.login==sqla.sql.bindparam('login')))

        self._sql_search = ptah.QueryFreezer(
            lambda: Session.query(cls) \
                .filter(sqla.sql.or_(
                    cls.email.contains(sqla.sql.bindparam('term')),
                    cls.name.contains(sqla.sql.bindparam('term'))))\
                .order_by(sqla.sql.asc('name')))

    def authenticate(self, creds):
        login, password = creds['login'], creds['password']

        user = self.get_bylogin(login)

        if user is not None:
            if ptah.pwd_tool.check(user.password, password):
                return user

    def get_principal_bylogin(self, login):
        return self.get_bylogin(login)

    def get(self, id):
        return self._sql_get.first(pid=id)

    def get_byuri(self, uri):
        return self._sql_get_uri.first(uri=uri)

    def get_bylogin(self, login):
        return self._sql_get_login.first(login=login)

    def change_password(self, principal, password):
        principal.password = password

    def search(self, term):
        for user in self._sql_search.all(term = '%%%s%%'%term):
            yield user


class CrowdUser(Base):

    __tablename__ = 'ptah_crowd'

    pid = sqla.Column(sqla.Integer, primary_key=True)
    __uri__ = sqla.Column('uri', sqla.Unicode(45),
                          unique=True, info={'uri': True})
    name = sqla.Column(sqla.Unicode(255))
    login = sqla.Column(sqla.Unicode(255), unique=True)
    email = sqla.Column(sqla.Unicode(255), unique=True)
    password = sqla.Column(sqla.Unicode(255))

    __uri_factory__ = ptah.UriFactory('user-crowd')

    def __init__(self, name, login, email, password=u''):
        super(CrowdUser, self).__init__()

        self.name = name
        self.login = login
        self.email = email
        self.password = password
        self.__uri__ = self.__uri_factory__()

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s<%s:%s>'%(self.__class__.__name__, self.name, self.__uri__)


def enable_provider(config, user=CrowdUser, searcher=None):
    provider = CrowdProvider(user)
    if searcher is None:
        searcher = provider.search

    config.ptah_auth_provider(
        user.__uri_factory__.schema, provider)
    config.ptah_password_changer(
        user.__uri_factory__.schema, provider.change_password)
    config.ptah_uri_resolver(
        user.__uri_factory__.schema, provider.get_byuri)
    config.ptah_principal_searcher(
        user.__uri_factory__.schema, searcher)
