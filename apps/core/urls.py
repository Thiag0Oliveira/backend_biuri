# -*- coding: utf-8 -*-

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.views.generic import TemplateView, View
from django.views.decorators.cache import cache_page
from .views import CreditCardCreate

from .views import CityList, Home, HomeProfissional, CreditCardCreateNew


##################################################


'''
	DJANGO URLS
'''

urlpatterns = [
                  url(r'^executivos$', cache_page(60)(Home.as_view()), name='home'),
                  url(r'^$', cache_page(60)(HomeProfissional.as_view()), name='home_profissional'),
                  url(r'^terms/$', cache_page(60)(TemplateView.as_view(template_name='userTerms.html')), name='terms'),
                  url(r'^citys/$', CityList.as_view(),name='city_list'),
                  url(r'^(?P<pk>[0-9]+)/creditcard/$', (CreditCardCreate.as_view()), name='creditcard-dashboard'),
                  url(r'^(?P<pk>[0-9]+)/payment/$', (CreditCardCreateNew.as_view()), name='creditcard-dashboard')
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
