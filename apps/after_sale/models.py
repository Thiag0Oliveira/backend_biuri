import requests
import json
from datetime import datetime, timedelta


from django.db import models
from apps.common.models import BestPraticesModel
from django.contrib.auth.models import User
from apps.customer.models import Customer
from apps.professional.models import Professional


# Create your models here.
from apps.service_core.models import Attendance


class Task(BestPraticesModel):
    """
    Agendor integration
    """
    attendance = models.ForeignKey('service_core.Attendance', null=True, blank=True, on_delete=models.DO_NOTHING)
    description = models.TextField(max_length=2000, blank=True)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.DO_NOTHING)
    type = models.CharField(max_length=20, choices=(('Profissional', 'Profissional'), ('Cliente', 'Cliente')))
    reason = models.CharField(max_length=40, choices=(('Dúvida', 'Dúvida'), ('Pesquisa de satisfação', 'Pesquisa de satisfação'), ('Reclamação', 'Reclamação'), ('Sugestão', 'Sugestão'), ('Cancelamento', 'Cancelamento'), ('Primeiro Atendimento', 'Primeiro Atendimento')))
    agendor_id = models.PositiveIntegerField(null=True, blank=True)

    def save(self, *args, **kwargs):
        task = super(Task, self).save(*args, **kwargs)
        if not self.agendor_id:
            days = 1
            if datetime.today().weekday() == 4:
                days = 3
            url = 'https://api.agendor.com.br/v1/tasks'
            headers = {"Content-Type": "application/json", 'Authorization': 'Token 38d083da-5fad-4cc2-8d1d-26c77fbf4738'}
            text = "Motivo: {} \n Descrição: {} \n \n".format(self.reason, self.description)
            user = self.user
            client = Customer.objects.none()
            if self.type == 'Cliente':
                client = Customer.objects.get(user=user)
            if self.type == 'Profissional':
                client = Professional.objects.get(user=user)
            if client:
                text += "Informações do {}: \n Nome: {} \n Telefone: {} \n Email: {} \n \n".format(self.type,
                                                                                                client.user.first_name,
                                                                                                client.celphone,
                                                                                                client.user.email)
            if self.attendance:
                text += "Atendimento {}: \n Serviço: {} \n Horário: {}\n \n".format(self.attendance.pk, self.attendance.initial_service, str(self.attendance.scheduling_date))
            data = {
                "organization": 14533390,
                "dueDate": str(datetime.now() + timedelta(days=days)),
                "text": text,
                "assignedUsers": [393854],
                }
            r = requests.post(url,json.dumps(data),headers=headers)
            r = r.json()
            self.agendor_id = r['taskId']
            task = super(Task, self).save(*args, **kwargs)
        return task