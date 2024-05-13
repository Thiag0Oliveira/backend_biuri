from django.db import models
from apps.common.models import BestPraticesModel


class State(BestPraticesModel):
    """
    Model for States
    """
    uf = models.CharField(max_length=2, unique=True)
    description = models.CharField(max_length=100, blank=True, null=True)
    cod_ibge = models.IntegerField(null=True)

    def __str__(self):
        return self.description


class City(BestPraticesModel):
    """
    Model for Cities of a State(:model:`core.state`)
    """
    name = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    state = models.ForeignKey(State,max_length=2, blank=True, null=True)
    latitude = models.DecimalField(max_digits=14, decimal_places=12, blank=True, null=True)
    longitude = models.DecimalField(max_digits=14, decimal_places=12, blank=True, null=True)
    cod_ibge = models.IntegerField(null=True)
    is_covered = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Neighborhood(BestPraticesModel):
    """
    Model for Neighborhoods of a City(:model:`core.city`)
    """
    description = models.CharField(max_length=100, blank=True, null=True)
    city = models.ForeignKey(City,blank=True, null=True)
    zone = models.CharField(max_length=100, blank=True, null=True)
    father = models.ForeignKey('self', null=True, blank=True)

    def __str__(self):
        return '{} - {}'.format(self.zone,self.description) if self.zone is not None else self.description


class Place(BestPraticesModel):
    """
    Model for a Place
    """
    cep = models.CharField(primary_key=True, max_length=10)
    description = models.CharField(max_length=200, blank=True, null=True)
    place_type = models.CharField(max_length=80, blank=True, null=True)
    latitude = models.DecimalField(max_digits=14, decimal_places=12, blank=True, null=True)
    longitude = models.DecimalField(max_digits=14, decimal_places=12, blank=True, null=True)
    city = models.ForeignKey(City,blank=True, null=True, on_delete=models.DO_NOTHING)
    neighborhood = models.ForeignKey(Neighborhood,blank=True, null=True, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.description


class Address(BestPraticesModel):
    """
    Model for an Address
    """
    place = models.ForeignKey(Place)
    address = models.CharField('Endereço',max_length=300)
    number = models.CharField('Número',max_length=20, null=True, blank=True)
    complement = models.CharField('Complemento',max_length=100, null=True, blank=True)
    reference_point = models.CharField('Pont de referência',max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=14, decimal_places=12, blank=True, null=True)
    longitude = models.DecimalField(max_digits=14, decimal_places=12, blank=True, null=True)
    cidade = models.ForeignKey(City, on_delete=models.DO_NOTHING)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.DO_NOTHING)
    state = models.ForeignKey(State, on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.address
