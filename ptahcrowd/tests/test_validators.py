import pform
import ptahcrowd
from ptah.testing import PtahTestCase


class TestCheckLogin(PtahTestCase):

    _includes = ('ptahcrowd',)

    def test_check_login(self):
        from ptahcrowd.provider import CrowdUser

        user = CrowdUser(username='username', email='email')
        CrowdUser.__type__.add(user)

        self.assertRaises(
            pform.Invalid, ptahcrowd.checkUsernameValidator, None, 'username')

        class Field(object):
            """ """

        field = Field()
        field.value = 'username'
        ptahcrowd.checkUsernameValidator(field, 'username')

        field.value = 'other-username'
        self.assertRaises(
            pform.Invalid, ptahcrowd.checkUsernameValidator, field, 'username')

    def test_lower(self):
        from ptahcrowd.schemas import lower

        self.assertEqual(lower('Tttt'), 'tttt')
        self.assertEqual(lower('tttT'), 'tttt')
        self.assertEqual(lower(lower), lower)
