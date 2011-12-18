import datetime
import transaction

import ptah
import ptah_crowd


class TestMemberprops(ptah.PtahTestCase):

    def test_memberprops_get(self):
        from ptah_crowd.memberprops import MemberProperties

        props = ptah_crowd.get_properties('uid1')

        self.assertIsInstance(props, MemberProperties)
        self.assertEqual(props.uri, 'uid1')
        self.assertEqual(props.validated, False)
        self.assertEqual(props.suspended, False)
        self.assertIsInstance(props.joined, datetime.datetime)

        props = ptah_crowd.get_properties('uid1')
        self.assertEqual(props.uri, 'uid1')

        self.assertEqual(
            ptah.get_session().query(MemberProperties).count(), 1)

    def test_memberprops_query(self):
        from ptah_crowd.memberprops import MemberProperties

        props = ptah_crowd.query_properties('uid1')
        self.assertIsNone(props)
        self.assertEqual(
            ptah.get_session().query(MemberProperties).count(), 0)

    def test_user_props(self):
        from ptah_crowd import CrowdUser
        from ptah_crowd.memberprops import MemberProperties

        user = CrowdUser(title='user-name', login='user-login',
                         email='user-email', password='passwd')

        self.assertIs(
            user.properties, ptah_crowd.query_properties(user.__uri__))
