""" member properties """
import ptah
import sqlalchemy as sqla
from datetime import datetime


def query_properties(uri):
    """ Query :py:class:`ptah_crowd.memberprops.UserProperties`
    properties for `uri`. If properties object is not found return ``None``.
    """
    return UserProperties._sql_get.first(uri=uri)


def get_properties(uri):
    """ Query :py:class:`ptah_crowd.memberprops.UserProperties`
    properties for `uri`. If properties object is not found create
    new properties object.
    """
    props = UserProperties._sql_get.first(uri=uri)
    if props is None:
        props = UserProperties(uri)
        Session = ptah.get_session()
        Session.add(props)
        Session.flush()
    return props


class UserProperties(ptah.get_base()):
    """ User properties

    ``uri``: Principal uri.

    ``joined``: Principal joined date.

    ``validated``: Is user validated or not.

    ``suspended``: Is user suspended or not. Suspended user can't login to
    system.

    ``data``: Additional data associated with principal. Data is ``dict`` type.

    """

    __tablename__ = 'ptah_crowd_memberprops'

    uri = sqla.Column(sqla.String(255), primary_key=True, info={'uri': True})
    joined = sqla.Column(sqla.DateTime())
    validated = sqla.Column(sqla.Boolean(), default=False)
    suspended = sqla.Column(sqla.Boolean(), default=False)
    data = sqla.Column(ptah.JsonDictType(), default={})

    def __init__(self, uri):
        super(UserProperties, self).__init__()

        self.uri = uri
        self.joined = datetime.now()
        self.validated = False
        self.suspended = False

    _sql_get = ptah.QueryFreezer(
        lambda: ptah.get_session().query(UserProperties)
        .filter(UserProperties.uri == sqla.sql.bindparam('uri')))
