import transaction
import ptah, ptah_crowd
from ptah import form
from ptah.testing import PtahTestCase
from pyramid.testing import DummyRequest


class TestCheckLogin(PtahTestCase):

    def test_check_login(self):
        from ptah_crowd import login
        from ptah_crowd.provider import CrowdUser, CrowdFactory

        user = CrowdUser(title='name', login='login', email='email')
        CrowdFactory().add(user)

        request = DummyRequest()

        self.assertRaises(
            form.Invalid, ptah_crowd.checkLoginValidator, None, 'login')

        class Field(object):
            """ """

        field = Field()
        field.value = 'login'
        ptah_crowd.checkLoginValidator(field, 'login')

        field.value = 'other-login'
        self.assertRaises(
            form.Invalid, ptah_crowd.checkLoginValidator, field, 'login')

    def test_lower(self):
        from ptah_crowd.schemas import lower

        self.assertEqual(lower('Tttt'), 'tttt')
        self.assertEqual(lower('tttT'), 'tttt')
        self.assertEqual(lower(lower), lower)
