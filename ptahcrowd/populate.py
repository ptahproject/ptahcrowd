import logging
import ptah
import ptahcrowd
from ptah.settings import SettingRecord


@ptah.populate(ptahcrowd.POPULATE_CREATE_ADMIN,
               title='Create admin user',
               requires=(ptah.POPULATE_DB_SCHEMA,))
def create_admin_user(registry):
    crowd_cfg = ptah.get_settings(ptahcrowd.CFG_ID_CROWD, registry)
    if not crowd_cfg['admin-login']:
        return

    session = ptah.get_session()
    ptah_cfg = ptah.get_settings(ptah.CFG_ID_PTAH, registry)

    rec = session.query(SettingRecord).filter(
        SettingRecord.name == 'ptahcrowd.admin-uri').first()
    if rec is not None:
        user = ptah.resolve(rec.value)
        if user is not None:
            return

    user = session.query(ptahcrowd.CrowdUser).\
           filter(ptahcrowd.CrowdUser.login==crowd_cfg['admin-login']).first()

    if user is None:
        tinfo = ptahcrowd.get_user_type(registry)

        log = logging.getLogger('ptahcrowd')
        log.info("Creating admin user `%s` %s",
                 crowd_cfg['admin-login'], crowd_cfg['admin-name'])

        # create user
        user = tinfo.create(
            name=crowd_cfg['admin-name'],
            login=crowd_cfg['admin-login'],
            email=ptah_cfg['email_from_address'])
        user.password = ptah.pwd_tool.encode(crowd_cfg['admin-password'])
        user.validated = True

        tinfo.add(user)

        if crowd_cfg['admin-role']:
            user.properties['roles'] = (crowd_cfg['admin-role'],)

        session.add(
            SettingRecord(name='ptahcrowd.admin-uri', value=user.__uri__))
