import logging
import ptah
import ptah_crowd
from pyramid.registry import Registry


@ptah.adapter(Registry, name=ptah_crowd.POPULATE_CREATE_ADMIN)
class CreateAdminUser(ptah.PopulateStep):

    title = 'Create admin user'
    requires = (ptah.POPULATE_DB_SCHEMA,)

    def execute(self):
        crowd_cfg = ptah.get_settings(ptah_crowd.CFG_ID_CROWD, self.registry)
        if not crowd_cfg['admin-login']:
            return

        Session = ptah.get_session()
        ptah_cfg = ptah.get_settings(ptah.CFG_ID_PTAH, self.registry)

        user = Session.query(ptah_crowd.CrowdUser).\
               filter(ptah_crowd.CrowdUser.login==crowd_cfg['admin-login']).\
               first()

        if user is None:
            tp = crowd_cfg['type']
            if not tp.startswith('cms-type:'):
                tp = 'cms-type:{0}'.format(tp)

            tinfo = ptah.resolve(tp)

            log = logging.getLogger('ptah_crowd')
            log.info("Creating admin user `%s` %s",
                     crowd_cfg['admin-login'], crowd_cfg['admin-name'])

            # create user
            user = tinfo.create(
                title=crowd_cfg['admin-name'],
                login=crowd_cfg['admin-login'],
                email=ptah_cfg['email_from_address'])
            user.password = ptah.pwd_tool.encode(crowd_cfg['admin-password'])

            ptah_crowd.CrowdFactory().add(user)
