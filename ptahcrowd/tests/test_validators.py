import transaction
import ptah, ptahcrowd
from ptah import form
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest


class TestCheckLogin(PtahTestCase):

    _includes = ('ptahcrowd',)

    def test_check_login(self):
        from ptahcrowd import login
        from ptahcrowd.provider import CrowdUser

        user = CrowdUser(name='name', login='login', email='email')
        CrowdUser.__type__.add(user)

        request = DummyRequest()

        self.assertRaises(
            form.Invalid, ptahcrowd.checkLoginValidator, None, 'login')

        class Field(object):
            """ """

        field = Field()
        field.value = 'login'
        ptahcrowd.checkLoginValidator(field, 'login')

        field.value = 'other-login'
        self.assertRaises(
            form.Invalid, ptahcrowd.checkLoginValidator, field, 'login')

    def test_lower(self):
        from ptahcrowd.schemas import lower

        self.assertEqual(lower('Tttt'), 'tttt')
        self.assertEqual(lower('tttT'), 'tttt')
        self.assertEqual(lower(lower), lower)
