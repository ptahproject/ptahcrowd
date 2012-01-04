import json
import sqlalchemy as sqla
from sqlalchemy.sql import select, delete
from datetime import datetime, timedelta
from velruse.utils import splitlines
from velruse.store.interface import UserStore

import ptah
import ptah_crowd


def includeme(config):
    settings = config.registry.settings

    # store
    config.registry.velruse_store = SQLStore()

    # providers
    providers = settings.get('velruse.providers', '')
    providers = splitlines(providers)

    for provider in providers:
        config.include(provider, route_prefix='/crowd-auth-provider')

    #cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD)


class KeyStorage(ptah.get_base()):
    __tablename__ = 'ptah_crowd_velruse_storage'

    key = sqla.Column(sqla.String(200), primary_key=True, nullable=False)
    value = sqla.Column(sqla.Text(), nullable=False)
    expires = sqla.Column(sqla.DateTime())


class SQLStore(UserStore):
    """Storage for Auth Provider"""

    def create(self):
        pass

    def retrieve(self, key):
        res = ptah.get_session().query(KeyStorage.value)\
            .filter(KeyStorage.key == key).first()
        if res is None:
            return None
        else:
            return json.loads(res.value)

    def store(self, key, value, expires=None):
        if expires:
            expiration = datetime.now() + timedelta(seconds=expires)
        value = json.dumps(value)

        ptah.get_session().add(
            KeyStorage(key=key, value=value, expires=expiration))
        return True

    def delete(self, key):
        ptah.get_session().query(KeyStorage)\
            .filter(KeyStorage.key == key).delete()
        return True

    def purge_expired(self):
        ptah.get_session().query(KeyStorage)\
            .filter(KeyStorage.expires < datetime.utcnow()).delete()
        return True
