#-*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import View
from django.contrib.auth.decorators import login_required


from .views import (
    CreateExecutiveLead, CreateProfissionalLead, UpdateExecutiveLead, UpdateProfissionalLead, ProfissionalLeadList,
	ProfissionalLeadUpdate, ProfissionalLeadCreate
)


##################################################


'''
	DJANGO URLS
'''

urlpatterns = [
	url(r'^executive/add/$', CreateExecutiveLead.as_view(), name='add_executive_lead'),
	url(r'^executive/update$', UpdateExecutiveLead.as_view(), name='update_executive_lead'),
	url(r'^profissional/add/$', CreateProfissionalLead.as_view(), name='add_profissional_lead'),
	url(r'^profissional/update$', UpdateProfissionalLead.as_view(), name='update_profissional_lead'),
	url(r'^lead/list', login_required(ProfissionalLeadList.as_view()), name='profissional_lead_list'),
	url(r'^lead/add', login_required(ProfissionalLeadCreate.as_view()), name='profissional_lead_create'),
	url(r'^lead/(?P<pk>[0-9]+)/edit$', login_required(ProfissionalLeadUpdate.as_view()), name='profissional_lead_update'),
	] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
