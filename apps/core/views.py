import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView, View, DetailView

from apps.service_core.models import Attendance

from apps.lead_captation.forms import (
    AddressLeadForm, ExecutiveLeadForm, ProfissionalLeadForm, SimpleExecutiveLeadForm,
    SimpleProfissionalLeadForm
)
from apps.payment.models import CreditCard
from apps.payment.forms import CreditCardForm
from .models import City


class Home(TemplateView):
    template_name='home.html'

    def get_context_data(self, **kwargs):
        context = super(Home, self).get_context_data(**kwargs)
        context['simpleleadform'] = SimpleExecutiveLeadForm()
        context['executiveleadform'] = ExecutiveLeadForm(prefix='modal')
        context['addressform'] = AddressLeadForm(prefix='address')
        return context

class HomeProfissional(TemplateView):
    template_name='home_profissional.html'

    def get_context_data(self, **kwargs):
        context = super(HomeProfissional, self).get_context_data(**kwargs)
        context['simpleleadform'] = SimpleProfissionalLeadForm()
        context['profissionalleadform'] = ProfissionalLeadForm(prefix='modal')
        context['addressform'] = AddressLeadForm(prefix='address')
        context['campaign'] = self.request.GET.get('campaign', None)
        return context


class CityList(View):
    def get(self, request, **kwargs):
        search = request.GET['term'].upper()
        data = {}
        cidades = City.objects.filter(name__startswith=search)
        data['items'] = list(cidades.values('id', 'name', 'state__uf'))
        return JsonResponse(data=data, status=200)


class CreditCardCreate(DetailView):
    model = Attendance
    form_class = CreditCardForm
    template_name = 'payment/payment_dashboard.html'
    queryset = Attendance.objects.select_related()


class CreditCardCreateNew(DetailView):
    model = Attendance
    form_class = CreditCardForm
    template_name = 'payment/payment_new.html'
    queryset = Attendance.objects.select_related()
