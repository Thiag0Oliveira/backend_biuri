#-*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import View
from django.contrib.auth.decorators import login_required


from apps.common.views import get_cep_json

from .views import DashboardHome, FormsExample, RelatorioProfissionais


##################################################


'''
	DJANGO URLS
'''

urlpatterns = [
	url(r'^$', login_required(DashboardHome.as_view()), name='dashboard_home'),
    url(r'^forms/$', FormsExample.as_view(), name='forms_example'),
    # url(r'^relatorio/$', RelatorioProfissionais.as_view(), name='relatorio_profissionais'),
    url(r'^service/cep/', get_cep_json, name="service-cep"),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
