from django.test import TestCase

from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from .models import CreditCard, PaymentForm


# class PaymentFormTestModel(TestCase):
#     """
#     Class to test the model PaymentForm
#     """
#     def setUp(self):
#         self.obj = mommy.make(PaymentForm)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, PaymentForm))
#         self.assertEqual(obj.__str__(), obj.description)
#
#
# class CreditCardTestModel(TestCase):
#     """
#     Class to test the model CreditCard
#     """
#     def setUp(self):
#         self.obj = mommy.make(CreditCard)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, CreditCard))
