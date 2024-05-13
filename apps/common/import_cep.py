from django.db import connections

from apps.core.models import City, Neighborhood, State

from .views import dictfetchall


def get_data(sql):
    cursor = connections['cepbr'].cursor()
    cursor.execute(sql)
    return dictfetchall(cursor)


def update_estados():
    sql = "select * from cepbr_estado;"
    data = get_data(sql)
    for item in data:
        state = State.objects.filter(cod_ibge=item['cod_ibge'])
        if state:
            state = state[0]
        else:
            state = State(cod_ibge=item['cod_ibge'])
        state.uf = item['uf']
        state.description = item['estado']
        state.save()
    return data

def update_citys():
    sql = "select * from cepbr_cidade;"
    data = get_data(sql)
    for item in data:
        city = City.objects.filter(cod_ibge=item['cod_ibge'])
        if city:
            city = city[0]
        else:
            city = City(cod_ibge=item['cod_ibge'])
        city.pk = item['id_cidade']
        city.state = State.objects.get(uf=item['uf'])
        city.name = item['cidade']
        city.save()
    return data

def update_neighborhood():
    sql = "select * from cepbr_bairro;"
    data = get_data(sql)
    for item in data:
        neighborhood = Neighborhood.objects.filter(id=item['id_bairro'])
        if neighborhood:
            neighborhood = neighborhood[0]
        else:
            neighborhood = Neighborhood(pk=item['id_bairro'])
        neighborhood.city = City.objects.get(pk=item['id_cidade'])
        neighborhood.description = item['bairro']
        neighborhood.save()
    return data

def update_cepbr():
    update_estados()
    update_citys()
    update_neighborhood()
    return 'sucess'
