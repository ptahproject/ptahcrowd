import sqlalchemy as sqla
from pyramid.decorator import reify
from pyramid.config import Configurator
from pyramid.events import ApplicationCreated

import ptah
from ptah.password import ID_PASSWORD_CHANGER
from ptah_crowd.settings import CFG_ID_CROWD
from ptah_crowd.memberprops import get_properties, query_properties

CROWD_APP_ID = 'ptah-crowd'


class CrowdUser(ptah.cms.BaseContent):
    """Default crowd user

    ``name``: User name.

    ``login``: User login.

    ``email``: User email.

    ``password``: User password.

    ``properties``: Instance of
    :py:class:`ptah_crowd.memberprops.UserProperties` class.

    """

    __tablename__ = 'ptah_crowd'

    __type__ = ptah.cms.Type(
        'ptah-crowd-user', 'Crowd user', global_allow = False)

    login = sqla.Column(sqla.Unicode(255), unique=True)
    email = sqla.Column(sqla.Unicode(255), unique=True)
    password = sqla.Column(sqla.Unicode(255))

    @property
    def name(self):
        return self.title

    @reify
    def properties(self):
        return get_properties(self.__uri__)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '%s<%s:%s>'%(self.__class__.__name__, self.title, self.__uri__)


class CrowdGroup(ptah.cms.BaseContent):
    """Crowd group

    ``name``: User name.

    ``users``: Users list.

    """

    login = ''

    __type__ = ptah.cms.Type(
        'ptah-crowd-group', 'Crowd group', global_allow = False)

    @property
    def name(self):
        return self.title


_sql_group_search = ptah.QueryFreezer(
    lambda: ptah.get_session().query(CrowdGroup) \
    .filter(CrowdUser.title.contains(sqla.sql.bindparam('term')))\
    .order_by(sqla.sql.asc('title')))

@ptah.principal_searcher('crowd-group')
def group_searcher(term):
    return _sql_group_search.all(term = '%%%s%%'%term)


@ptah.roles_provider('crowd')
def crowd_user_roles(context, uid, registry):
    """ crowd roles provider

    return user default roles and user group roles"""
    roles = set()

    props = query_properties(uid)
    if props is not None:
        roles.update(props.data.get('roles',()))

        for grp in props.data.get('groups',()):
            roles.update(ptah.get_local_roles(grp, context))

    return roles


def get_user_type(registry=None):
    cfg = ptah.get_settings(CFG_ID_CROWD, registry)
    tp = cfg['type']
    if not tp.startswith('cms-type:'):
        tp = 'cms-type:{0}'.format(tp)

    return ptah.resolve(tp)


def get_allowed_content_types(context, registry=None):
    cfg = ptah.get_settings(CFG_ID_CROWD, registry)
    return (cfg['type'],)


class CrowdApplication(ptah.cms.BaseApplicationRoot,ptah.cms.BaseContainer):
    """Ptah crowd application, you should never directly create
    instances of this class. Use :py:data:`ptah_crowd.CrowdFactory` instead.
    """

    __type__ = ptah.cms.Type('ptah-crowd-provider',
                             'Ptah user management',
                             filter_content_types = True,
                             allowed_content_types = get_allowed_content_types)

    def add(self, user):
        """ Add user to crowd application. """
        Session = ptah.get_session()
        Session.add(user)
        Session.flush()

        name = str(user.__id__)
        if isinstance(user, CrowdGroup):
            name = 'group_{0}'.format(name)

        self[name] = user

    def get_user_bylogin(self, login):
        """ Given a login string return a user """
        return CrowdAuthProvider._sql_get_login.first(login=login)


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
