from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [
    url(r'^$', login_required(views.CompanyList.as_view()), name='company-list'),
    url(r'^create$', login_required(views.CompanyCreate.as_view()), name='company-create'),
    url(r'^(?P<pk>[0-9]+)/edit$', login_required(views.CompanyUpdate.as_view()),
        name='company-update'),
    url(r'^sale$', login_required(views.SaleList.as_view()), name='sale-list'),
    url(r'^sale/create$', login_required(views.SaleCreate.as_view()), name='sale-create'),
    url(r'^sale/(?P<pk>[0-9]+)/edit$', login_required(views.SaleUpdate.as_view()),
        name='sale-update'),
    url(r'^data/(?P<pk>[0-9]+)/', views.GetCompany.as_view(), name='api_company'),
    ]
