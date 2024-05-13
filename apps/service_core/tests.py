from django.test import TestCase

from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from .models import Attendance, AttendanceService, Category, Service


# class CategoryTestModel(TestCase):
#     """
#     Class to test the model Category
#     """
#     def setUp(self):
#         self.obj = mommy.make(Category)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, Category))
#         self.assertEqual(obj.__str__(), obj.name)
#
#
# class ServiceTestModel(TestCase):
#     """
#     Class to test the model Service
#     """
#     def setUp(self):
#         self.obj = mommy.make(Service)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, Service))
#         self.assertEqual(obj.__str__(), obj.name)
#
#
# class AttendanceTestModel(TestCase):
#     """
#     Class to test the model Attendance
#     """
#     def setUp(self):
#         self.obj = mommy.make(Attendance)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, Attendance))
#
#
# class AttendanceServiceTestModel(TestCase):
#     """
#     Class to test the model AttendanceService
#     """
#     def setUp(self):
#         self.obj = mommy.make(AttendanceService)
#
#     def test_obj_creation_mommy(self):
#         obj = self.obj
#         self.assertTrue(isinstance(obj, AttendanceService))
