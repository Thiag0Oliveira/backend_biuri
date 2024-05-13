from django.db import models
from apps.common.models import BestPraticesModel


# Create your models here.

class ProfessionalVisualisation(BestPraticesModel):
    """
    Stores in app Visualizations of Professionals(:model:`professional.professional`) from Customers(:model:`customer.customer`)
    """
    professional = models.ForeignKey('professional.Professional', on_delete=models.DO_NOTHING)
    customer = models.ForeignKey('customer.Customer', on_delete=models.DO_NOTHING, null=True, blank=True)
    attendance = models.ForeignKey('service_core.Attendance', on_delete=models.DO_NOTHING, null=True, blank=True,
                                   related_name='attendance_visualizations')
    type = models.CharField(max_length=10, choices=(('profile', 'Perfil'), ('list', 'Listagem'), ('search', 'Busca')))
    position = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{}".format(self.id)