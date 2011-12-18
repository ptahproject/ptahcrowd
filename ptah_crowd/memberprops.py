""" member properties """
import ptah
import sqlalchemy as sqla
from datetime import datetime


def query_properties(uri):
    return MemberProperties._sql_get.first(uri=uri)


def get_properties(uri):
    props = MemberProperties._sql_get.first(uri=uri)
    if props is None:
        props = MemberProperties(uri)
        Session = ptah.get_session()
        Session.add(props)
        Session.flush()
    return props


class MemberProperties(ptah.get_base()):

    __tablename__ = 'ptah_crowd_memberprops'

    uri = sqla.Column(sqla.Unicode, primary_key=True, info={'uri': True})
    joined = sqla.Column(sqla.DateTime())
    validated = sqla.Column(sqla.Boolean, default=False)
    suspended = sqla.Column(sqla.Boolean(), default=False)
    data = sqla.Column(ptah.JsonDictType(), default={})

    def __init__(self, uri):
        super(MemberProperties, self).__init__()

        self.uri = uri
        self.joined = datetime.now()
        self.validated = False
        self.suspended = False

    _sql_get = ptah.QueryFreezer(
        lambda: ptah.get_session().query(MemberProperties)
        .filter(MemberProperties.uri == sqla.sql.bindparam('uri')))
