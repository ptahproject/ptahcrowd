import sqlalchemy as sqla
from datetime import datetime
from pyramid.compat import text_type

import pform
import ptah
from ptah.password import passwordValidator
from ptahcrowd.settings import CFG_ID_CROWD
from ptahcrowd.schemas import lower
from ptahcrowd.schemas import checkLoginValidator
from ptahcrowd.schemas import checkEmailValidator
from ptahcrowd import const
from ptahcrowd.settings import _

CROWD_APP_ID = 'ptah-crowd'


@ptah.tinfo('ptah-crowd-user', 'Crowd user')

class CrowdUser(ptah.get_base()):
    """Default crowd user

    ``name``: User name.

    ``login``: User login.

    ``email``: User email.

    ``password``: User password.

    ``properties``: User properties.

    """

    __tablename__ = 'ptahcrowd_users'

    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode(255), info={
        'title': const.NAME_TITLE,
        'description': const.NAME_DESCR,
    })
    login = sqla.Column(sqla.Unicode(255), unique=True, info={
        'title': const.LOGIN_TITLE,
        'description': const.LOGIN_DESCR,
        'preparer': lower,
        'validator': checkLoginValidator,
    })
    email = sqla.Column(sqla.Unicode(255), unique=True, info={
        'title': const.EMAIL_TITLE,
        'description': const.EMAIL_DESCR,
        'preparer': lower,
        'validator': pform.All(pform.Email(), checkEmailValidator),
    })
    joined = sqla.Column(sqla.DateTime(), info={'skip': True})
    password = sqla.Column(sqla.Unicode(255), info={
        'title': const.PASSWORD_TITLE,
        'description': const.PASSWORD_DESCR,
        'validator': passwordValidator,
        'field_type': 'password'
    })
    validated = sqla.Column(sqla.Boolean(), info={
        'title': _('Validated'),
        'default': False,
    })
    suspended = sqla.Column(sqla.Boolean(), info={
        'title': _('Suspended'),
        'default': False,
    })
    properties = sqla.Column(ptah.JsonDictType(), default={})

    def __init__(self, **kw):
        self.joined = datetime.utcnow()
        self.properties = {}

        super(CrowdUser, self).__init__(**kw)

    def __str__(self):
        return self.name

    def __name__(self):
        return str(self.id)

    def __repr__(self):
        return '%s<%s:%s>'%(self.__class__.__name__, self.name, self.__uri__)

    _sql_get_id = ptah.QueryFreezer(
        lambda: ptah.get_session().query(CrowdUser)\
            .filter(CrowdUser.id==sqla.sql.bindparam('id')))

    @classmethod
    def get_byid(cls, id):
        return cls._sql_get_id.first(id=id)


@ptah.tinfo('ptah-crowd-group', 'Crowd group')

class CrowdGroup(ptah.get_base()):
    """Crowd group

    ``title``: Group title.

    ``description``: Group description.

    ``users``: Users list.

    """

    __tablename__ = 'ptahcrowd_groups'

    id = sqla.Column(sqla.Integer, primary_key=True)
    name = sqla.Column(sqla.Unicode(255))
    description = sqla.Column(sqla.UnicodeText, default=text_type(''),
                              info = {'missing': '', 'field_type': 'textarea',
                                      'default': '', 'required': False})

    _sql_get_id = ptah.QueryFreezer(
        lambda: ptah.get_session().query(CrowdGroup)\
            .filter(CrowdGroup.id==sqla.sql.bindparam('id')))

    @classmethod
    def get_byid(cls, id):
        return cls._sql_get_id.first(id=id)


_sql_group_search = ptah.QueryFreezer(
    lambda: ptah.get_session().query(CrowdGroup) \
    .filter(CrowdGroup.name.contains(sqla.sql.bindparam('term')))\
    .order_by(sqla.sql.asc('name')))

@ptah.principal_searcher('crowd-group')
def group_searcher(term):
    return _sql_group_search.all(term = '%%%s%%'%term)


@ptah.roles_provider('crowd')
def crowd_user_roles(context, uid, registry):
    """ crowd roles provider

    return user default roles and user group roles"""
    roles = set()

    props = getattr(ptah.resolve(uid), 'properties', None)
    if props is not None:
        roles.update(props.get('roles',()))

        for grp in props.get('groups',()):
            roles.update(ptah.get_local_roles(grp, context))

    return roles


def get_user_type(registry=None):
    cfg = ptah.get_settings(CFG_ID_CROWD, registry)
    tp = cfg['type']
    if not tp.startswith('type:'):
        tp = 'type:{0}'.format(tp)

    return ptah.resolve(tp)


def get_allowed_content_types(context, registry=None):
    cfg = ptah.get_settings(CFG_ID_CROWD, registry)
    return (cfg['type'],)


@ptah.auth_provider('ptah-crowd-auth')
class CrowdAuthProvider(object):

    _sql_get_login = ptah.QueryFreezer(
        lambda: ptah.get_session().query(CrowdUser)\
            .filter(CrowdUser.login==sqla.sql.bindparam('login')))

    _sql_get_email = ptah.QueryFreezer(
        lambda: ptah.get_session().query(CrowdUser)\
            .filter(CrowdUser.email==sqla.sql.bindparam('email')))

    _sql_search = ptah.QueryFreezer(
        lambda: ptah.get_session().query(CrowdUser) \
            .filter(sqla.sql.or_(
                CrowdUser.name.contains(sqla.sql.bindparam('term')),
                CrowdUser.email.contains(sqla.sql.bindparam('term'))))\
            .order_by(sqla.sql.asc('name')))

    def authenticate(self, creds):
        login, password = creds['login'], creds['password']

        user = self._sql_get_login.first(login=login)
        if not user:
            user = self._sql_get_email.first(email=login)

        if user is not None:
            if ptah.pwd_tool.check(user.password, password):
                return user

    def get_principal_bylogin(self, login):
        return self._sql_get_login.first(login=login)

    def get_principal_byemail(self, email):
        return self._sql_get_email.first(email=email)

    @classmethod
    def search(cls, term):
        for user in cls._sql_search.all(term = '%%%s%%'%term):
            yield user

    def add(self, user):
        """ Add user to crowd application. """
        Session = ptah.get_session()
        Session.add(user)
        Session.flush()

        return user

    def get_user_bylogin(self, login):
        """ Given a login string return a user """
        return self._sql_get_login.first(login=login)


@ptah.password_changer('ptah-crowd-user')
def change_password(principal, password):
    principal.password = password

ptah.principal_searcher.register(
    'ptah-crowd-user', CrowdAuthProvider.search)
