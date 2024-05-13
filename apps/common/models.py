from django.contrib.auth.models import User
from django.db import models

from django_extensions.db.models import TimeStampedModel
from model_utils.models import SoftDeletableModel
from simple_history.models import HistoricalRecords


# Create your models here.

class BestPraticesModel(SoftDeletableModel):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Address(BestPraticesModel):
    """
    Model for Addresses
    """
    postal_code = models.CharField('CEP',max_length=8)
    address = models.CharField('Endereço',max_length=200, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    number = models.CharField('Número',max_length=120, blank=True, null=True)
    neighborhood = models.CharField('Bairro',max_length=120, blank=True, null=True)
    city = models.CharField('Cidade',max_length=120, blank=True, null=True)
    state = models.CharField('Estado',max_length=120, blank=True, null=True)

    def __str__(self):
        return self.postal_code


class UserAddress(BestPraticesModel):
    """
    Stores the Address(:model:`common.address`) of a given User
    """
    user = models.ForeignKey(User)
    name = models.CharField('Descricao Endereco', max_length=20, blank=True, default='Casa')
    postal_code = models.CharField('CEP', max_length=8)
    address = models.CharField('Endereço', max_length=200, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    number = models.CharField('Número', max_length=120, blank=True, null=True)
    neighborhood = models.CharField('Bairro', max_length=120, blank=True, null=True)
    city = models.CharField('Cidade', max_length=120, blank=True, null=True)
    state = models.CharField('Estado', max_length=120, blank=True, null=True)
    latitude = models.DecimalField('Latitude', max_digits=14, decimal_places=12, null=True, blank=True)
    longitude = models.DecimalField('Latitude', max_digits=14, decimal_places=12, null=True, blank=True)
    ref_point = models.CharField('Ponto de Referencia', max_length=500, blank=True, null=True)


    def __str__(self):
        return "CEP: {} - {}, {} {} {}, {}-{}".format(self.postal_code,
                                                      self.address,
                                                      self.number,
                                                      self.complemento if self.complemento else '',
                                                      self.neighborhood,
                                                      self.city,
                                                      self.state)

GENDER_LIST = (
    ('', 'Sexo'),
    ('Masculino', 'Masculino'),
    ('Feminino', 'Feminino'),
)

CIVIL_STATUS_LIST = (
    ('', 'Estado civil'),
    ('Solteiro(a)', 'Solteiro(a)'),
    ('Casado(a)', 'Casado(a)'),
    ('Viúvo(a)', 'Viúvo(a)'),
    ('Divorciado(a)', 'Divorciado(a)'),
    ('Outro', 'Outro'),
)
