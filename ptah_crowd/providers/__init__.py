import json
import ptah
import sqlalchemy as sqla
from datetime import datetime, timedelta


class AuthenticationComplete(object):
    """An AuthenticationComplete context object"""

    def __init__(self, profile=None, credentials=None):
        """Create an AuthenticationComplete object with user data"""
        self.profile = profile
        self.credentials = credentials


class Storage(ptah.get_base()):

    __tablename__ = 'ptah_crowd_auth_storage'

    key = sqla.Column(sqla.String(200), primary_key=True, nullable=False)
    value = sqla.Column(sqla.Text(), nullable=False)
    expires = sqla.Column(sqla.DateTime())

    @classmethod
    def retrieve(cls, key):
        res = ptah.get_session().query(cls.value).filter(cls.key == key).first()
        if res is None:
            return None
        else:
            return json.loads(res.value)

    @classmethod
    def store(cls, key, value, expires=None):
        if expires:
            expiration = datetime.utcnow() + timedelta(seconds=expires)
        value = json.dumps(value)

        ptah.get_session().add(cls(key=key, value=value, expires=expiration))
        return True

    @classmethod
    def delete(cls, key):
        ptah.get_session().query(cls).filter(cls.key == key).delete()
        return True

    @classmethod
    def purge_expired(cls):
        ptah.get_session().query(cls)\
            .filter(cls.expires < datetime.utcnow()).delete()
        return True
