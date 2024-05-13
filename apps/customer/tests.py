from django.test import TestCase, Client

from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from .models import Customer


# class CustomerTestModel(TestCase):
#     """
#     Class to test the model Customer
#     """
#     def setUp(self):
#         self.obj = mommy.make(Customer)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, Customer))
#         self.assertEqual(obj.__str__(), obj.user.first_name)
#
#
# class TestLoginCustomer(TestCase):
#     def test_login(self):
#         c = Client()
#         response = c.post(path='/api/accounts/login/',
#                           data='email=teste%403ysoftwarehouse.com.br&password=1234abcd&professional=false',
#                           content_type='application/x-www-form-urlencoded')
#         self.assertTrue(response.status_code, 200)