from django.test import TestCase

from model_mommy import mommy

from .models import ExecutiveLead, Lead, ProfissionalLead


# Create your tests here.

class ModelTestCase(TestCase):
    model = Lead
    def test_model(self):
        instace_model = mommy.make(self.model)
        self.assertTrue(isinstance(instace_model, self.model))
        self.assertEqual(instace_model.__str__(), instace_model.name)

class ModelTestExecutiveLead(ModelTestCase):
    model = ExecutiveLead

class ModelTestProfissionalLead(ModelTestCase):
    model = ProfissionalLead
