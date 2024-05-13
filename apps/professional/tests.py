from django.test import TestCase

from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from .models import FavoriteProfessional, Professional, Schedule, ServiceProfessional


# class ProfessionalTestModel(TestCase):
#     """
#     Class to test the model Professional
#     """
#     def setUp(self):
#         self.obj = mommy.make(Professional)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, Professional))
#         self.assertEqual(obj.__str__(), obj.user.first_name)
#
#
# class ScheduleTestModel(TestCase):
#     """
#     Class to test the model Schedule
#     """
#     def setUp(self):
#         self.obj = mommy.make(Schedule)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, Schedule))
#         self.assertEqual(obj.__str__(), obj.daily_schedule)
#
#
# class FavoriteProfessionalTestModel(TestCase):
#     """
#     Class to test the model FavoriteProfessional
#     """
#     def setUp(self):
#         self.obj = mommy.make(FavoriteProfessional)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, FavoriteProfessional))
#
#
# class ServiceProfessionalTestModel(TestCase):
#     """
#     Class to test the model ServiceProfessional
#     """
#     def setUp(self):
#         self.obj = mommy.make(ServiceProfessional)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, ServiceProfessional))
