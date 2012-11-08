import pform
import ptahcrowd
from ptah.testing import PtahTestCase


class TestCheckLogin(PtahTestCase):

    _includes = ('ptahcrowd',)

    def test_check_login(self):
        from ptahcrowd.provider import CrowdUser

        user = CrowdUser(name='name', login='login', email='email')
        CrowdUser.__type__.add(user)

        self.assertRaises(
            pform.Invalid, ptahcrowd.checkLoginValidator, None, 'login')

        class Field(object):
            """ """

        field = Field()
        field.value = 'login'
        ptahcrowd.checkLoginValidator(field, 'login')

        field.value = 'other-login'
        self.assertRaises(
            pform.Invalid, ptahcrowd.checkLoginValidator, field, 'login')

    def test_lower(self):
        from ptahcrowd.schemas import lower

        self.assertEqual(lower('Tttt'), 'tttt')
        self.assertEqual(lower('tttT'), 'tttt')
        self.assertEqual(lower(lower), lower)
