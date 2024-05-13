import json

import requests
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string

from simple_history.models import HistoricalRecords

from apps.common.models import CIVIL_STATUS_LIST, GENDER_LIST, Address, BestPraticesModel
from apps.service_core.models import Category
from apps.professional.models import Executive
from apps.payment.models import Campaign


# Create your models here.
LEAD_TYPES = (
    ('Profissional', 'Profissional'),
    ('Executive', 'Executive'),
)

LEAD_STATUS = (
    ('-', '-'),
    ('Pendente de contato', 'Pendente de contato'),
    ('Contato realizado', 'Contato realizado'),
    ('Visita agendada', 'Visita agendada'),
    ('Cadastro completo', 'Cadastro completo'),
    ('Ativado', 'Ativado'),
    ('Desvinculado', 'Desvinculado'),
    ('Sem interesse', 'Sem interesse'),
)

class Lead(BestPraticesModel):
    """
    Model for Generic Leads
    """
    name = models.CharField(max_length=200, verbose_name='Nome')
    cpf = models.CharField(max_length=11, blank=True, verbose_name='CPF')
    rg = models.CharField(max_length=11, blank=True, verbose_name='RG')
    email = models.EmailField(blank=True, verbose_name='E-Mail')
    address = models.ForeignKey(Address, null=True, blank=True, verbose_name='Endereço')
    type = models.CharField(max_length=20, choices=LEAD_TYPES, blank=True)
    status = models.CharField(max_length=20, choices=LEAD_STATUS, default='-', verbose_name='Status')
    gender = models.CharField(max_length=20, choices=GENDER_LIST, blank=True, verbose_name='Gênero')
    civil_status = models.CharField(max_length=20, choices=CIVIL_STATUS_LIST, blank=True, verbose_name='Estado Civil')
    birthdate = models.DateField(null=True, blank=True, verbose_name='Data de Aniversário')
    category = models.ManyToManyField(Category, blank=True, verbose_name='Categorias')
    telephone = models.CharField(max_length=11, blank=True, verbose_name='Telefone')
    celphone = models.CharField(max_length=11, blank=True, verbose_name='Celular')
    is_completed = models.BooleanField(default=False)
    obs = models.TextField(max_length=1000, blank=True, verbose_name='Observações')
    history = HistoricalRecords()
    indicated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Indicado por')
    executive = models.ForeignKey(Executive, null=True, blank=True, verbose_name='Executivo')
    campaign = models.ForeignKey(Campaign, null=True, blank=True, verbose_name='Campanha')

    def __str__(self):
        return self.name


class ProfissionalLead(Lead):
    """
    Model for Professional Leads
    """

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        
        if(not self.pk):
            url = 'https://api.agendor.com.br/v3/people/upsert'
            headers = {"Content-Type": "application/json", 'Authorization': 'Token 38d083da-5fad-4cc2-8d1d-26c77fbf4738'}
            email = '{}@teste.com'.format(self.telephone)
            data = {}
            if self.email:
                email = self.email
            lead_origin = 985050
            if self.indicated_by:
                lead_origin = 985048
                data['role'] = self.indicated_by.pk
            data = {
                "name": self.name + " - NOVO",
                "leadOrigin": lead_origin,
                "description": self.obs,
                "contact": {
                    "email": email,
                    "mobile": self.telephone,
                    }
                }
            requests.post(url,json.dumps(data),headers=headers)
        return super(ProfissionalLead, self).save(*args, **kwargs)

class ExecutiveLead(Lead):
    """
    Model for Executive Leads
    """

    def __str__(self):
        return self.name
