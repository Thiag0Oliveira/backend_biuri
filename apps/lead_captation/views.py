import json

from django.core import serializers
from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, ListView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.db import transaction

from pycpfcnpj import cpfcnpj

from apps.payment.models import Campaign
from .forms import (
    AddressLeadForm, ExecutiveLeadForm, ProfissionalLeadForm, SimpleExecutiveLeadForm,
    SimpleProfissionalLeadForm
)
from .models import ExecutiveLead, ProfissionalLead, Lead

from apps.professional.models import Executive
from apps.common.views import PermissionUpdateView


class CreateLead(View):
    """
    View for Lead creation
    """
    model = None
    type = None
    form = SimpleExecutiveLeadForm

    def post(self, request, *args, **kwargs):
        data = {}
        executive = request.POST.get('executive-id', None)
        telephone = request.POST.get('telephone', None)
        campaign = request.GET.get('campaign', None)
        cpf = request.POST.get('cpf', None)
        post = request.POST.copy()
        post['telephone'] = telephone.replace('(','').replace(')','').replace('-','').replace(' ','')
        if cpf is not None:
            post['cpf'] = cpf.replace('.', '').replace('-', '')
        request.POST = post
        form = self.form(request.POST)
        if form.is_valid():
            obj = form.save()
            obj.type = self.type
            campaigns = Campaign.objects.filter(slug=campaign)
            if campaigns.exists():
                campaign = campaigns[0]
                obj.campaign = campaign
                obj.executive = campaign.executive
            obj.save()
            data = {'id': obj.id, 'name': obj.name, 'email':obj.email, 'telephone': telephone}
            return JsonResponse(data, status=200, content_type='application/json')
        else:
            data = {'error': 'interno', 'message': 'Erro interno'}
            return JsonResponse(data, status=500, content_type='application/json')


class CreateExecutiveLead(CreateLead):
    """
    View for Executive Lead(:mode:`lead_captation.ExecutiveLead`) creation
    """
    model = ExecutiveLead
    type = 'Executive'
    form = SimpleExecutiveLeadForm


class UpdateExecutiveLead(View):
    """
    View for Executive Lead(:mode:`lead_captation.ExecutiveLead`) update
    """

    def post(self, request, *args, **kwargs):
        data = {}
        executive = request.POST.get('executive-id', None)
        instance = ExecutiveLead.objects.get(id=executive)
        
        cpf = request.POST.get('modal-cpf', None)
        telephone = request.POST.get('modal-telephone', None)
        celphone = request.POST.get('modal-celphone', None)
        cep = request.POST.get('address-postal_code', None)
        
        post = request.POST.copy()
        post['modal-cpf'] = cpf.replace('.','').replace('-','')
        post['modal-telephone'] = telephone.replace('(','').replace(')','').replace('-','').replace(' ','')
        post['modal-celphone'] = celphone.replace('(','').replace(')','').replace('-','').replace(' ','')
        post['address-postal_code'] = cep.replace('-','')
        request.POST = post
       
        form = ExecutiveLeadForm(request.POST, instance=instance, prefix='modal')
        addressform = AddressLeadForm(request.POST, prefix='address')
       
        if not cpfcnpj.validate(cpf):
            data = {'error': 'cpf', 'message': 'CPF inválido'}
            return JsonResponse(data, status=500, content_type='application/json')
        if form.is_valid() and addressform.is_valid():
            address =  addressform.save(commit=False)         
            address.save()          
            obj = form.save(commit=False)
            obj.address = address            
            obj.save()
            data = {'id': obj.id, 'name': obj.name, 'cpf': cpf, 'email':obj.email} 
            return JsonResponse(data, status=200, content_type='application/json')
        else:
            data = {'error': 'interno', 'message': 'Error interno'}
            return JsonResponse(data, status=500, content_type='application/json')


# class CreateProfissionalLead(View):
#
#     def post(self, request, *args, **kwargs):
#         data = {}
#         profissional = request.POST.get('profissional-id', None)
#         cpf = request.POST.get('cpf', None)
#         post = request.POST.copy()
#         post['cpf'] = cpf.replace('.','').replace('-','')
#         request.POST = post
#         form = SimpleProfissionalLeadForm(request.POST)
#
#         if not cpfcnpj.validate(cpf):
#             data = {'error': 'cpf', 'message': 'CPF inválido'}
#             return JsonResponse(data, status=500, content_type='application/json')
#         if profissional:
#             obj = ProfissionalLead.objects.get(id=profissional)
#             data = {'id': obj.id, 'name': obj.name, 'cpf': cpf, 'email':obj.email}
#             return JsonResponse(data, status=200, content_type='application/json')
#         if form.is_valid():
#             obj = form.save()
#             obj.type = 'Profissional'
#             obj.save()
#             data = {'id': obj.id, 'name': obj.name, 'cpf': cpf, 'email':obj.email}
#             return JsonResponse(data, status=200, content_type='application/json')
#         else:
#             data = {'error': 'interno', 'message': 'Error interno'}
#             return JsonResponse(data, status=500, content_type='application/json')

class CreateProfissionalLead(CreateLead):
    """
    View for Professional Lead(:mode:`lead_captation.ProfessionalLead`) creation
    """
    model = ProfissionalLead
    type = 'Profissional'
    form = SimpleProfissionalLeadForm


class UpdateProfissionalLead(View):
    """
    View for Professional Lead(:mode:`lead_captation.ProfessionalLead`) update
    """
    def post(self, request, *args, **kwargs):
        data = {}
        profissional = request.POST.get('profissional-id', None)
        instance = ProfissionalLead.objects.get(id=profissional)
        
        cpf = request.POST.get('modal-cpf', None)
        telephone = request.POST.get('modal-telephone', None)
        celphone = request.POST.get('modal-celphone', None)
        cep = request.POST.get('address-postal_code', None)
        
        post = request.POST.copy()
        post['modal-cpf'] = cpf.replace('.','').replace('-','')
        post['modal-telephone'] = telephone.replace('(','').replace(')','').replace('-','').replace(' ','')
        post['modal-celphone'] = celphone.replace('(','').replace(')','').replace('-','').replace(' ','')
        post['address-postal_code'] = cep.replace('-','')
        request.POST = post
       
        form = ProfissionalLeadForm(request.POST, instance=instance, prefix='modal')
        addressform = AddressLeadForm(request.POST, prefix='address')

        if form.is_valid() and addressform.is_valid():
            address =  addressform.save(commit=False)         
            address.save()          
            obj = form.save(commit=False)
            obj.address = address            
            obj.save()
            data = {'id': obj.id, 'name': obj.name, 'cpf': cpf, 'email':obj.email} 
            return JsonResponse(data, status=200, content_type='application/json')
        else:
            data = {'error': 'interno', 'message': 'Error interno'}
            return JsonResponse(data, status=500, content_type='application/json')


class ProfissionalLeadList(ListView):
    """
    Lists Professional Leads(:model:`lead_captation.Lead`)
    """
    model = Lead
    queryset = Lead.objects.all()
    template_name = 'lead/lead_list.html'
    paginate_by = 10
    ordering = '-id'

    def get_ordering(self):
        ordering = self.request.GET.get('order_by', self.ordering)
        return ordering

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.has_perm('service_core.change_attendance'):
            return super(ProfissionalLeadList, self).dispatch(request, *args, **kwargs)
        return HttpResponseNotFound('<h1>Page not found</h1>')

    def get_queryset(self):
        queryset = super(ProfissionalLeadList, self).get_queryset().prefetch_related('category')
        user_executive = self.user_executive()
        if user_executive is not None:
             queryset = queryset.filter(executive=user_executive)
        return queryset


class ProfissionalLeadUpdate(UpdateView):
    """
    View for Professional Lead(:mode:`lead_captation.Lead`) update
    """
    model = Lead
    form_class = ProfissionalLeadForm
    template_name = 'lead/profissional_lead_form.html'
    success_url = reverse_lazy('lead:profissional_lead_list')
    queryset = Lead.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProfissionalLeadUpdate, self).get_context_data(**kwargs)
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        if form.is_valid():
            object = form.save()
            if object.executive is None:
                object.executive = self.user_executive()
                object.save()
            return super(ProfissionalLeadUpdate, self).form_valid(form)
        context = {'form': form}
        return render(request, self.template_name, context)

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            user_executive = self.user_executive()
            if user_executive is not None:
                pk = kwargs.get('pk', None)
                get_object_or_404(Lead.objects.filter(executive=user_executive), pk=pk)
        return super().dispatch(*args, **kwargs)


class ProfissionalLeadCreate(CreateView):
    """
    View for Professional Lead(:mode:`lead_captation.Lead`) creation
    """
    model = Lead
    form_class = ProfissionalLeadForm
    template_name = 'lead/profissional_lead_form.html'
    success_url = reverse_lazy('lead:profissional_lead_list')

    def get_context_data(self, **kwargs):
        context = super(ProfissionalLeadCreate, self).get_context_data(**kwargs)
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self.object = form.save()
            return super(ProfissionalLeadCreate, self).form_valid(form)
        context = {'form': form}
        return render(request, self.template_name, context)
