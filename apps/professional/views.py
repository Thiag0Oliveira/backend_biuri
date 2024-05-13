import datetime

import requests
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO
import pandas as pd
import numpy as np
from unicodedata import normalize

from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg, Count, F, Sum, DateField
from django.db.models.functions import Cast
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.contrib.auth.decorators import login_required, permission_required
from oauth2_provider.models import AccessToken
from django.template.loader import render_to_string
from django.template import Context, Template
from django_pandas.io import read_frame

from apps.common.models import UserAddress
from apps.common.views import GenericFilterList, Sms, generator_code, render_pdf_view, PermissionListView, PermissionUpdateView, PermissionCreateView
from apps.core.forms import AddressForm, CustomUserForm, CustomCustomerUserForm, UserAddressForm, CustomCustomerUserFormWhitoutUsername
from apps.core.models import City, Neighborhood
from apps.customer.models import Customer
from apps.payment.forms import BankAccountForm
from apps.payment.forms import CreditCard as CreditCardModel
from apps.service_core.models import Attendance, PricingCriterionOptions, Service, AttendanceService, PricingCriterion
from apps.service_core.tasks import generate_schedule_professional_new, regenerate_schedule_professional_new
from apps.common.scrapper import get_user_information
from .mixins import TypeUserMixin

from .filters import GenericFilter, PortfolioFilter

from .forms import (
    ProfessionalCategoryForm, ProfessionalCityForm, ProfessionalCityFormSet, ProfessionalForm,
    ProfessionalPricingCriterionServiceForm, ProfessionalServiceForm, ServiceProfessionalForm,
    ServiceProfessionalFormset, ProfessionalScheduleDefaultForm, ProfessionalCriterionForm, ExecutiveForm,
    ProfessionalDocumentForm, SellerForm,
    ProfessionalConciergeForm, ProfessionalConciergeFormPost, AttendanceForm, CustomerForm, AttendanceConciergeForm,
    PushScheduleForm)

from .models import (Calendar,
                     Executive, Professional, ProfessionalBadge, ProfessionalCategory, ProfessionalCity, ExecutiveCity,
                     ProfessionalEvaluation, Schedule, ServiceProfessional, ServiceProfessionalPricingCriterion,
                     ProfessionalScheduleDefault,
                     ProfessionalCriterion, ProfessionalDocument, Seller, Contract, ContractClause,
                     ServiceProfessionalLog, ProfessionalPicture
                     )
from ..message_core.models import PushSchedule, PushScheduleCity


def process_scheduling_shock_calendar(professional):
    attendances = Attendance.objects.filter(professional_id=professional, status='waiting_confirmation')
    c = Calendar()
    for attendance in attendances:
        disponibility = c.has_disponibility(professional=professional,
                            date=attendance.scheduling_date.date(),
                            hour_inicial=attendance.scheduling_date.time(),
                            hour_final=attendance.expected_date_checkout.time())
        if not disponibility:
            attendance.status = 'scheduling_shock'
            attendance.save()
    return {}

# Create your views here.


class ProfessionalPermissionExecutiveMixin(object):

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def get_queryset(self):
        queryset = super().get_queryset()
        executive = self.user_executive()
        if self.request.user.is_superuser:
            return queryset
        if executive is not None:
            return queryset.filter(executive=executive)
        else:
            return queryset.none()

class ProfessionalPermissionListExecutiveMixin(object):

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None


class ProfessionalPermissionExecutiveMixin(ProfessionalPermissionListExecutiveMixin):

    def dispatch(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            executive = self.user_executive()
            if executive is not None:
                pk = kwargs.get('pk', None)
                get_object_or_404(Professional.objects.filter(executive=executive),pk=pk)
        return super().dispatch(*args, **kwargs)


class ProfessionalList(PermissionListView, ProfessionalPermissionListExecutiveMixin, GenericFilterList):
    """
    Lists the Professionals(:model:`professional.Professional`)
    """
    paginate_by = 2
    ordering = 'id'
    model = Professional
    template_filter_name = 'professional/professional_filter.html'
    template_name = 'professional/professional_list2.html'
    filterset_class = GenericFilter
    verbose_name = 'Profissional'
    verbose_name_plural = 'Profissionais'
    add_display_name = 'Adicionar Profissional'
    queryset = Professional.objects.select_related('user','category')
    ordering = ['user__first_name']
    # list_display = ['id', 'rating', 'user__first_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        executive = self.user_executive()
        if self.request.user.is_superuser:
            return queryset
        if executive is not None:
            return queryset.filter(executive=executive)
        else:
            return queryset.none()

class ProfessionalPriceLogList(PermissionListView, ProfessionalPermissionListExecutiveMixin, generic.ListView):
    """
    Lists the Professional Price Logs(:model:`professional.ServiceProfessionalLog`)
    """
    paginate_by = 50
    ordering = '-created'
    model = ServiceProfessionalLog
    queryset = ServiceProfessionalLog.objects.select_related('professional','service')
    permission_required = 'professional.change_professional'

    def get_queryset(self):
        queryset = super().get_queryset()
        executive = self.user_executive()
        if self.request.user.is_superuser:
            return queryset
        if executive is not None:
            return queryset.filter(professional__executive=executive)
        else:
            return queryset.none()


class ProfessionalPortfolio(PermissionListView, ProfessionalPermissionListExecutiveMixin, GenericFilterList):
    """
    Displays information related to registered Professionals(:model:`professional.Professional`)
    """
    paginate_by = 2
    ordering = 'id'
    model = Professional
    template_filter_name = 'professional/professional_filter.html'
    template_name = 'professional/professional_portfolio.html'
    filterset_class = PortfolioFilter
    verbose_name = 'Profissional'
    verbose_name_plural = 'Profissionais'
    add_display_name = 'Adicionar Profissional'
    queryset = Professional.objects.select_related('user','category')
    ordering = ['user__first_name']
    # list_display = ['id', 'rating', 'user__first_name']

    def get_queryset(self):
        queryset = super().get_queryset().filter(professional_enabled=True, professional_enabled_executive=True)
        executive = self.user_executive()
        if self.request.user.is_superuser:
            return queryset
        if executive is not None:
            return queryset.filter(executive=executive)
        else:
            return queryset.none()

    def get_context_data(self, **kwargs):
        context = super(ProfessionalPortfolio, self).get_context_data(**kwargs)
        executive = self.user_executive()
        if executive is not None:
            del self.filterset.form.fields['executive']
        context['professional_categories'] = self.object_list.all().values('category__name').annotate(y=Count('id')).order_by('-y')
        categorias = self.request.GET.getlist('categorias')
        if len(categorias) > 0:
            context['professional_services'] = self.object_list.filter(services__isnull=False, services__service__category_id__in = categorias).values('services__service__name').annotate(y=Count('id', distinct=True),media_minimum=Avg('services__minimum_price'),media_maximum=Avg('services__maximum_price'),media_tempo=Avg('services__average_time')).order_by('-y')
        else:
            context['professional_services'] = self.object_list.filter(services__isnull=False).values('services__service__name').annotate(y=Count('id', distinct=True),media_minimum=Avg('services__minimum_price'),media_maximum=Avg('services__maximum_price'),media_tempo=Avg('services__average_time')).order_by('-y')
        context['professional_dates'] = self.object_list.values('created').annotate(y=Count('id')).order_by('created')
        df = read_frame(self.object_list.values('created', 'executive__user__first_name', 'id'), fieldnames=['id', 'executive__user__first_name'], index_col='created')
        df.index = pd.to_datetime(df.index)
        df['date'] = df.index.date
        df = pd.pivot_table(df, columns='executive__user__first_name', values='id', index='date', aggfunc='count', fill_value=0)
        df = df.reindex(pd.date_range(start='1/10/2018', end=datetime.date.today()), fill_value=0)
        for column in df:
            df[column] = df[column].cumsum()
        context['date_professional'] = df.to_html(table_id='date-professional')
        return context

class ProfessionalConcierge(ProfessionalPermissionListExecutiveMixin, generic.ListView):
    """
    View used to search for available Professionals(:model:`professional.Professional`) to manually create Attendances(:model:`service_core.Attendance`)
    """
    paginate_by = 2
    ordering = 'id'
    template_name = 'professional/professional_concierge.html'
    model = Professional
    form = ProfessionalConciergeForm
    form_post = ProfessionalConciergeFormPost
    queryset = Professional.objects.all()

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset().all()
        form = self.form(request.GET)
        profissionais = []
        if form.is_valid():
            service_time = datetime.timedelta(minutes=form.cleaned_data['service'].mean_range_time)
            profissionais = self.get_queryset().filter(professional_enabled=True, professional_enabled_executive=True).select_related('user') \
                .filter(services__service=form.cleaned_data['service'], services__is_removed=False,
                        citys__city=form.cleaned_data['city'])
            if form.cleaned_data['neighborhood'] is not None:
                profissionais = profissionais.filter(citys__neighborhoods__id=form.cleaned_data['neighborhood'].id)
            if form.cleaned_data['price_min']:
                profissionais = profissionais.filter(services__service=form.cleaned_data['service'],services__minimum_price__gte=form.cleaned_data['price_min'])
            if form.cleaned_data['price_max']:
                profissionais = profissionais.filter(services__service=form.cleaned_data['service'],services__minimum_price__lte=form.cleaned_data['price_max'])
            if form.cleaned_data['date']:
                profissionais = profissionais.filter(schedules__attendance__isnull=True,
                                  schedules__is_removed=False,
                                  schedules__daily_date=form.cleaned_data['date']).distinct()
            else:
                profissionais = profissionais.filter(schedules__attendance__isnull=True,
                                                     schedules__is_removed=False,
                                                     schedules__daily_date__gte=datetime.date.today()).distinct()
            if form.cleaned_data['time']:
                time_final = datetime.datetime.combine(datetime.date.today(), form.cleaned_data['time']) + service_time
                profissionais = profissionais.filter(
                        schedules__daily_time_begin__lte=form.cleaned_data['time'],
                        schedules__daily_time_end__gte=time_final.time())
            profissionais = list(profissionais.order_by('full_name').values())
            for profissional in profissionais:
                service_professional = ServiceProfessional.objects.filter(professional_id=profissional['id'],
                                                                          service=form.cleaned_data['service'])
                pricing_criterion = form.cleaned_data['pricing_criterion']
                if pricing_criterion is not None:
                    price = ServiceProfessionalPricingCriterion.objects.filter(service_professional=service_professional,
                                                                       pricingcriterionoptions=pricing_criterion)[0].price
                else:
                    price = service_professional[0].minimum_price
                profissional['price'] = price
                schedule = Schedule.objects.filter(professional_id=profissional['id'],
                                                   attendance__isnull=True)
                if form.cleaned_data['date']:
                    schedule = schedule.filter(daily_date=form.cleaned_data['date'])
                else:
                    schedule = schedule.filter(daily_date__gte=datetime.date.today())
                if form.cleaned_data['time']:
                    time_final = datetime.datetime.combine(datetime.date.today(),
                                                           form.cleaned_data['time']) + service_time
                    schedule = schedule.filter(daily_time_begin__lte=form.cleaned_data['time'],
                                              daily_time_end__gte=time_final.time())
                if schedule.exists():
                    profissional['schedules'] = schedule.order_by('daily_date', 'daily_time_begin')[:5]
        context = self.get_context_data()
        context['form'] = form
        context['form_post'] = self.form_post()
        context['object_list'] = profissionais
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.form_post(request.POST)
        form_get = self.form(request.GET)
        if form.is_valid() and form_get.is_valid():
            attendance = Attendance()
            attendance.initial_service = form_get.cleaned_data['service']
            attendance.neighborhood = form_get.cleaned_data['neighborhood']
            attendance.scheduling_date = form.cleaned_data['scheduling_date']
            attendance.professional_id = form.cleaned_data['professional']
            attendance.type = 'has_preference'
            celphone = form.cleaned_data['celphone']
            name = form.cleaned_data['name']
            customer = Customer.objects.filter(celphone=celphone)
            if customer.exists():
                attendance.customer = customer[0]
                credit_cards = CreditCardModel.objects.filter(customer=customer[0]).order_by('-created')
                if credit_cards.exists():
                    attendance.credit_card = credit_cards[0]
            else:
                user = User.objects.filter(username=celphone)
                if user.exists():
                    user = user[0]
                else:
                    user = User(username=celphone, email = celphone + '@email.com.br', first_name = name)
                    user.save()
                    password = celphone[-4:]
                    user.set_password(password)
                    user.save()
                customer = Customer(celphone=celphone, user=user)
                customer.save()
                attendance.customer = customer
            attendance.save()
            service_attendance = AttendanceService()
            service_attendance.attendance = attendance
            service_attendance.service = attendance.initial_service
            service_attendance.price = form.cleaned_data['price']
            service_attendance.duration = form_get.cleaned_data['service'].mean_range_time
            service_attendance.save()
            url = '/dashboard/professional/concierge/' + str(attendance.pk) + '/'
            return JsonResponse({'url': url}, status=200)
        return HttpResponse({}, status=404)


class ProfessionalConciergeCreate(generic.UpdateView):
    """
    View used to manually create Attendances(:model:`service_core.Attendance`)
    """
    model = Attendance
    form_class = AttendanceForm
    template_name = 'professional/professional_concierge_form.html'
    queryset = Attendance.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ProfessionalConciergeCreate, self).get_context_data(**kwargs)
        # context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        context['user_form'] = CustomCustomerUserForm(prefix='user_form', instance=self.object.customer.user)
        context['customer_form'] = CustomerForm(prefix='customer_form', instance=self.object.customer)
        context['concierge_form'] = AttendanceConciergeForm(prefix='concierge_form')
        context['concierge_form'].fields['address'].queryset = UserAddress.objects.filter(user=self.object.customer.user)
        context['address_form'] = UserAddressForm(prefix='address_form')
        context['user_form'].fields['username'].label = 'Usuário'
        # context['bank_account_form'] = BankAccountForm(prefix='bank_account_form', instance=self.object.bank_account)
        # context['professional_document_form'] = self.professional_document_form(prefix='professional_document_form',
        #                                                                         queryset=ProfessionalDocument.objects.
        #                                                                         filter(professional_id=self.object))
        # executive = self.user_executive()
        # if executive is not None:
        #     citys = executive.get_citys.values_list('city__id', flat=True)
        #     context['form'].fields['cidades'].queryset = context['form'].fields['cidades'].queryset.filter(pk__in=citys)
        return context


    def post(self, request, *args, **kwargs):
        context = dict()
        object = self.get_object()
        form = AttendanceForm(request.POST, instance=object)
        user_form = CustomCustomerUserFormWhitoutUsername(request.POST, instance=object.customer.user, prefix='user_form')
        customer_form = CustomerForm(request.POST, instance=object.customer, prefix='customer_form')
        concierge_form = AttendanceConciergeForm(request.POST, prefix='concierge_form')
        address_form = UserAddressForm(request.POST, prefix='address_form')

        if form.is_valid() and user_form.is_valid() and customer_form.is_valid() and concierge_form.is_valid():
                attendance = form.save()
                user = user_form.save()
                customer_form.save()
                if concierge_form.cleaned_data['address'] is not None:
                    attendance.address = concierge_form.cleaned_data['address']
                    attendance.save()
                    url = '/after_sale/attendance/' + str(attendance.pk) + '/edit'
                    return redirect(url)
                else:
                    if address_form.is_valid():
                        address = address_form.save(commit=False)
                        address.user = user
                        address.save()
                        attendance.address = address
                        attendance.save()
                        url = '/after_sale/attendance/' + str(attendance.pk) + '/edit'
                        return redirect(url)
        print(form.errors, user_form.errors, customer_form.errors, concierge_form.errors, address_form.errors)
        context['form'] = form
        context['user_form'] = user_form
        context['customer_form'] = customer_form
        context['concierge_form'] = concierge_form
        context['address_form'] = address_form
        return render(request,self.template_name,context)


class ProfessionalUpdateCategory(PermissionUpdateView, ProfessionalPermissionExecutiveMixin, View):
    """
    View used to update the Professional Categories(:model:`professional.ProfessionalCategory`) and the Professional Cities(:model:`professional.ProfessionalCity`) of a given Professional(:model:`professional.Professional`)
    """
    model = ProfessionalCategory
    template_name = 'professional/professional_category.html'
    categoryprofessional = modelformset_factory(ProfessionalCategory,
                                                form=ProfessionalCategoryForm, can_delete=False, exclude=['professional'], extra=0)
    cityprofessional = modelformset_factory(ProfessionalCity, form=ProfessionalCityForm, can_delete=False, extra=0)
    # criterionprofessional = modelformset_factory(ProfessionalCriterion, form=ProfessionalCriterionForm, can_delete=False, extra=0)
    permission_required = 'professional.change_professional'


    def get(self, request, *args, **kwargs):
        context={}
        pk = kwargs.get('pk', None)
        if pk is None:
            if request.user.is_anonymous():
                token = request.GET.get('auth_token', None)
                if token is not None:
                    access_token = get_object_or_404(AccessToken, token=token)
                    pk = Professional.objects.get(user=access_token.user).pk
                else:
                    raise Http404("Página não encontrada")
            else:
                pk = Professional.objects.get(user=request.user).pk
        formset = self.categoryprofessional(queryset=ProfessionalCategory.objects.select_related('category').prefetch_related('services').filter(professional_id=pk))
        cityprofessional = self.cityprofessional(queryset=ProfessionalCity.objects.select_related('city').prefetch_related('neighborhoods').filter(professional_id=pk),prefix='cityprofessional')
        # criterionprofessional = self.criterionprofessional(queryset=ProfessionalCriterion.objects.
        #                                                    select_related('pricing_criterion').prefetch_related('pricing_criterion_option').
        #                                                    filter(professional_id=pk),prefix='criterionprofessional')
        context['form'] = formset
        context['cityprofessional'] = cityprofessional
        # context['criterionprofessional'] = criterionprofessional
        return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        context={}
        formset = self.categoryprofessional(request.POST)
        cityprofessional = self.cityprofessional(request.POST, prefix='cityprofessional')
        # criterionprofessional = self.criterionprofessional(request.POST, prefix='criterionprofessional')
        context['form'] = formset
        context['cityprofessional'] = cityprofessional
        # context['criterionprofessional'] = criterionprofessional
        # if formset.is_valid() and criterionprofessional.is_valid() and cityprofessional.is_valid():
        if formset.is_valid() and cityprofessional.is_valid():
            formset.save()
            cityprofessional.save()
            # criterionprofessional.save()
            pk = kwargs.get('pk', None)
            if pk is None:
                url = '/dashboard/professional/service'
                if request.user.is_anonymous():
                    token = request.GET.get('auth_token', None)
                    if token is not None:
                        access_token = get_object_or_404(AccessToken, token=token)
                        pk = Professional.objects.get(user=access_token.user).pk
                        url = '/dashboard/professional/service' + '?auth_token=' + token
                    else:
                        raise Http404("Página não encontrada")
                else:
                    pk = Professional.objects.get(user=request.user).pk
            else:
                url = '/dashboard/professional/' + str(pk) + '/service'
            professional_category = self.model.objects.filter(professional_id=pk).values_list('services')
            services = ServiceProfessional.objects.filter(professional_id = pk).exclude(service__in=list(professional_category))
            services.delete()
            service_category_models = []
            for service_category in professional_category:
                service = Service.objects.get(pk=service_category[0])
                service_update = ServiceProfessional.objects.filter(service=service, professional_id = pk)
                if not service_update:
                    service_professional = ServiceProfessional(service=service, professional_id=pk,
                                                                maximum_price=service.minimal_range_price,
                                                               minimum_price=service.minimal_range_price,
                                                                average_time=service.mean_range_time)
                    service_category_models.append(service_professional)
            ServiceProfessional.objects.bulk_create(service_category_models)

            services = ServiceProfessional.objects.filter(professional_id=pk).values_list('service', flat=True)
            service_criterions = Service.objects.filter(id__in=services).values_list('pricing_criterion', flat=True)
            clean_criterions = [i for i in service_criterions if i]
            criterions = ProfessionalCriterion.objects.filter(professional_id=pk).exclude(pricing_criterion_id__in=clean_criterions)
            criterions.delete()
            for criterion in clean_criterions:
                professional = Professional.objects.get(id=pk)
                ProfessionalCriterion.objects.get_or_create(professional=professional,
                                                            pricing_criterion_id=criterion)
            return redirect(url)
        return render(request,self.template_name,context)


class ProfessionalUpdateService(PermissionUpdateView,ProfessionalPermissionExecutiveMixin, View):
    """
    View used to update the Professional Services(:model:`professional.ServiceProfessional`) and the Professional Criterion(:model:`professional.ServiceProfessionalPricingCriterion`) of a given Professional(:model:`professional.Professional`)
    """
    model = ServiceProfessional
    template_name = 'professional/professional_service.html'
    service_professional = modelformset_factory(ServiceProfessional,
                                                form=ProfessionalServiceForm, can_delete=True, exclude=['professional'], extra=0)
    permission_required = 'professional.change_professional'
    criterionprofessional = modelformset_factory(ProfessionalCriterion, form=ProfessionalCriterionForm, can_delete=False, extra=0)

    def get(self, request, *args, **kwargs):
        context={}
        pk = kwargs.get('pk', None)
        if pk is None:
            if request.user.is_anonymous():
                token = request.GET.get('auth_token', None)
                if token is not None:
                    access_token = get_object_or_404(AccessToken, token=token)
                    pk = Professional.objects.get(user=access_token.user).pk
                else:
                    raise Http404("Página não encontrada")
            else:
                pk = Professional.objects.get(user=request.user).pk
        formset = self.service_professional(queryset=ServiceProfessional.objects.select_related('service__category').filter(professional_id=pk, service_id__can_set_price=True).order_by('service__category__name', 'service__name', 'service__gender'))
        services = ServiceProfessional.objects.filter(professional_id=pk).values_list('service', flat=True)
        service_criterions = Service.objects.filter(id__in=services).values_list('pricing_criterion', flat=True)
        criterionprofessional = self.criterionprofessional(queryset=ProfessionalCriterion.objects.
                                                           select_related('pricing_criterion').prefetch_related('pricing_criterion_option').
                                                           filter(professional_id=pk), prefix='criterionprofessional')

        context['form'] = formset
        context['criterionprofessional'] = criterionprofessional
        return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        context={}
        formset = self.service_professional(request.POST)
        criterionprofessional = self.criterionprofessional(request.POST, prefix='criterionprofessional')
        # choosenCriterions = ProfessionalCriterion.objects.filter(request.POST.getlist('criterionprofessional'))
        context['form'] = formset
        context['criterionprofessional'] = criterionprofessional
        print(criterionprofessional)
        print(request.POST)
        if formset.is_valid() and criterionprofessional.is_valid():
            formset.save()
            criterionprofessional.save()
            pk = kwargs.get('pk', None)
            token = request.GET.get('auth_token', None)
            if pk is None:
                url = '/dashboard/professional/service_pricing'
                if request.user.is_anonymous():
                    if token is not None:
                        access_token = get_object_or_404(AccessToken, token=token)
                        pk = Professional.objects.get(user=access_token.user).pk
                        url = '/dashboard/professional/service_pricing' + '?auth_token=' + token
                    else:
                        raise Http404("Página não encontrada")
                else:
                    pk = Professional.objects.get(user=request.user).pk
            else:
                url = '/dashboard/professional/' + str(pk) + '/service_pricing'
            services_professional = self.model.objects.filter(professional_id=pk)
            actual_services_created = services_professional.values_list('pk', flat=True)
            services = ServiceProfessionalPricingCriterion.objects.filter(service_professional__professional_id=pk)\
                .exclude(service_professional__pk__in=list(actual_services_created))
            services.delete()
            criterions = ProfessionalCriterion.objects.filter(professional_id=pk)
            option_list = []
            for criterion in criterions:
                option_list = option_list + list(criterion.pricing_criterion_option.all().values_list('id', flat=True))
            removed_criterions = ServiceProfessionalPricingCriterion.objects.filter(
                service_professional__professional_id=pk).exclude(pricingcriterionoptions_id__in=option_list)
            removed_criterions.delete()
            for service in services_professional:
                if service.service.pricing_criterion is not None:
                    pricing_criterions = service.service.pricing_criterion.options.all().order_by('id')
                    professional_criterion = ProfessionalCriterion.objects.filter(
                        pricing_criterion=service.service.pricing_criterion, professional_id=service.professional)
                    if professional_criterion.exists():
                        professional_criterion = professional_criterion[0]
                        pricing_criterions = professional_criterion.pricing_criterion_option.all()
                    len_pricing_criterion = len(pricing_criterions)
                    range_price_add = 0
                    if len_pricing_criterion > 1:
                        range_price_add = (service.maximum_price - service.minimum_price) / (len_pricing_criterion - 1)
                    count = 0
                    for option in pricing_criterions:
                        option_query = ServiceProfessionalPricingCriterion.objects.filter(service_professional=service,
                                                                                          pricingcriterionoptions=option)
                        new_price = round(service.minimum_price + (count * range_price_add), 0)
                        if option_query.exists():
                            option_query.update(price=new_price, average_time=service.average_time)
                        else:
                            pricing_criterion = ServiceProfessionalPricingCriterion(service_professional=service,
                                                                                    pricingcriterionoptions=option,
                                                                                    price=new_price,
                                                                                    average_time=service.average_time)
                            pricing_criterion.save()
                        count += 1
                # if service.service.pricing_criterion is not None:
                #     for criterion in option_list:
                #         pricing_criterion_option = PricingCriterionOptions.objects.get(id=criterion)
                #
                #         new_criterion = ServiceProfessionalPricingCriterion.objects.filter(service_professional=service, pricingcriterionoptions=pricing_criterion_option)
                #         if len(new_criterion) == 0:
                #             new_service_professional_criterion = ServiceProfessionalPricingCriterion(
                #                 service_professional=service, pricingcriterionoptions=pricing_criterion_option, price=service.minimum_price)
                #             new_service_professional_criterion.save()
            return redirect(url)
        print(criterionprofessional.errors)
        return render(request,self.template_name,context)


class ProfessionalUpdatePortfolio(PermissionUpdateView,ProfessionalPermissionExecutiveMixin, View):
    """
    View for Displaying, Uploading and Deleting Pictures(:model:`professional.ProfessionalPicture`) for Professional Portfolios
    """
    model = ProfessionalPicture
    template_name = 'professional/professional_picture_portfolio_form.html'
    permission_required = 'professional.change_professional'

    def get(self, request, *args, **kwargs):
        context={}
        pk = kwargs.get('pk', None)
        context['pictures'] = ProfessionalPicture.objects.filter(professional_id=pk)
        return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        context={}
        lenFiles = len(request.FILES)
        # print(request.FILES)
        if lenFiles > 0:
            for file in request.FILES:
                real_file = request.FILES.get(file)
                pk = kwargs.get('pk', None)
                p = ProfessionalPicture(professional_id=pk,picture=real_file,picture_thumbnail=real_file)
                p.save()
        return render(request,self.template_name,context)


class ProfessionalUpdatePricingCriterion(PermissionUpdateView,ProfessionalPermissionExecutiveMixin, View):
    """
    View used to update Professional Service Prices for Services with Pricing Criterion(:model:`professional.ServiceProfessionalPricingCriterion`)
    """
    model = ServiceProfessionalPricingCriterion
    template_name = 'professional/professional_pricing_criterion.html'
    service_professional = modelformset_factory(ServiceProfessionalPricingCriterion,
                                                form=ProfessionalPricingCriterionServiceForm, can_delete=True, exclude=['professional'], extra=0)
    permission_required = 'professional.change_professional'

    def get(self, request, *args, **kwargs):
        context={}
        pk = kwargs.get('pk', None)
        if pk is None:
            if request.user.is_anonymous():
                token = request.GET.get('auth_token', None)
                if token is not None:
                    access_token = get_object_or_404(AccessToken, token=token)
                    pk = Professional.objects.get(user=access_token.user).pk
                else:
                    raise Http404("Página não encontrada")
            else:
                pk = Professional.objects.get(user=request.user).pk
        formset = self.service_professional(queryset=ServiceProfessionalPricingCriterion.objects.select_related(
            'service_professional__service__category', 'pricingcriterionoptions').filter(
            service_professional__professional_id=pk, service_professional_id__service_id__can_set_price=True).order_by('service_professional__service__category__name',
                                                               'service_professional__service__name', 'service_professional__service__gender',
                                                               'pricingcriterionoptions__id'))
        context['form'] = formset
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        context={}
        formset = self.service_professional(request.POST)
        context['form'] = formset
        pk = kwargs.get('pk', None)
        if pk is None:
            if request.user.is_anonymous():
                token = request.GET.get('auth_token', None)
                if token is not None:
                    access_token = get_object_or_404(AccessToken, token=token)
                    pk = Professional.objects.get(user=access_token.user).pk
                else:
                    raise Http404("Página não encontrada")
            else:
                pk = Professional.objects.get(user=request.user).pk
        if formset.is_valid():
            formset.save()
            professional = Professional.objects.get(pk=pk)
            if not professional.send_sms:
                generate_schedule_professional_new(professional.pk)
                professional.send_sms = True
                professional.save()
            url = '/dashboard/professional'
            return redirect(url)
        return render(request,self.template_name,context)


class ProfessionalScheduleDefaultUpdate(PermissionUpdateView,ProfessionalPermissionExecutiveMixin, View):
    """
    View used to update a Professional Schedule(:model:`professional.ProfessionalScheduleDefault`)
    """
    model = ProfessionalScheduleDefault
    template_name = 'professional/professional_sheddule_default.html'
    schedule_default = modelformset_factory(ProfessionalScheduleDefault,
                                                form=ProfessionalScheduleDefaultForm, can_delete=True, exclude=['professional'], extra=0)
    permission_required = 'professional.change_professional'

    def get(self, request, *args, **kwargs):
        context={}
        pk = kwargs.get('pk', None)
        if pk is None:
            if request.user.is_anonymous():
                token = request.GET.get('auth_token', None)
                if token is not None:
                    access_token = get_object_or_404(AccessToken, token=token)
                    pk = Professional.objects.get(user=access_token.user).pk
                else:
                    raise Http404("Página não encontrada")
            else:
                pk = Professional.objects.get(user=request.user).pk
        formset = self.schedule_default(queryset=ProfessionalScheduleDefault.objects.filter(professional_id=pk).order_by('day_of_week'))
        context['form'] = formset
        return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        context={}
        formset = self.schedule_default(request.POST)
        context['form'] = formset
        if formset.is_valid():
            formset.save()
            pk = kwargs.get('pk', None)
            regenerate_schedule_professional_new(pk)
            url = '/dashboard/professional'
            return redirect(url)
        return render(request,self.template_name,context)


class ProfessionalCreate(PermissionCreateView, generic.CreateView):
    """
    View for Professional Creation
    """
    model = Professional
    form_class = ProfessionalForm
    template_name = 'professional/professional_form2.html'
    permission_form_fields = [{'field': 'professional_enabled', 'permission': 'can_liberate_professional'},
                              {'field': 'executive', 'permission': 'can_edit_executive'}]

    def permission_form(self, form, user):
        for permission_form_field in self.permission_form_fields:
            if not user.has_perm(permission_form_field['permission']):
                del form.fields[permission_form_field['field']]
        return form

    def get_success_url(self):
        url = '/dashboard/professional/' + str(self.object.pk) + '/category'
        return url

    def get_context_data(self, **kwargs):
        context = super(ProfessionalCreate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        context['user_form'] = CustomUserForm(prefix='user_form')
        context['address_form'] = AddressForm(prefix='address_form')
        context['bank_account_form'] = BankAccountForm(prefix='bank_account_form')
        executive = self.user_executive()
        if executive is not None:
            citys = executive.get_citys.values_list('city__id', flat=True)
            context['form'].fields['cidades'].queryset = context['form'].fields['cidades'].queryset.filter(pk__in=citys)
        return context

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        form = self.permission_form(form=form, user=self.request.user)
        address_form = AddressForm(request.POST, prefix="address_form")
        user_form = CustomUserForm(request.POST, prefix='user_form')
        bank_account_form = BankAccountForm(request.POST, prefix='bank_account_form')

        if form.is_valid() and address_form.is_valid() and user_form.is_valid() and bank_account_form.is_valid():
            executive = Executive.objects.filter(user=request.user)
            user = user_form.save()
            self.object = form.save(commit=False)
            self.object.user = user
            address = address_form.save(commit=False)
            address.save()
            bank_account = bank_account_form.save(commit=False)
            bank_account.save()
            self.object.address = address
            self.object.bank_account = bank_account
            if executive:
                executive = executive[0]
                self.object.executive = executive
            self.object = form.save()
            category_professional_models = []
            for category in form.data.getlist('categorias'):
                category_profissional = ProfessionalCategory(professional=self.object, category_id = category)
                category_professional_models.append(category_profissional)
            ProfessionalCategory.objects.bulk_create(category_professional_models)
            badge_professional_models = []
            for badge in form.data.getlist('badges'):
                badge_professional = ProfessionalBadge(professional=self.object, badge_id = badge)
                badge_professional_models.append(badge_professional)
            ProfessionalBadge.objects.bulk_create(badge_professional_models)
            city_professional_models = []
            for city in form.data.getlist('cidades'):
                city_professional = ProfessionalCity(professional=self.object, city_id=city)
                city_professional_models.append(city_professional)
            ProfessionalCity.objects.bulk_create(city_professional_models)
            pricing_criterion_professional = list(ProfessionalCategory.objects.filter(professional=self.object,
                                                                                      category__service__pricing_criterion__isnull=False) \
                                                  .values_list('category__service__pricing_criterion',
                                                               flat=True).distinct())
            for pricing_criterion in pricing_criterion_professional:
                ProfessionalCriterion.objects.get_or_create(professional=self.object,
                                                            pricing_criterion_id=pricing_criterion)
            days_of_week = form.data.getlist('days_of_week')
            professional_sheddule_default_models = []
            for day in days_of_week:
                professional_sheddule_default = ProfessionalScheduleDefault(professional=self.object,
                                                                                day_of_week=day, provide_all_day=True)
                professional_sheddule_default_models.append(professional_sheddule_default)
            ProfessionalScheduleDefault.objects.bulk_create(professional_sheddule_default_models)
            return super(ProfessionalCreate, self).form_valid(form)
        return render(request, self.template_name, {'form': form, 'address_form': address_form, 'user_form': user_form, 'bank_account_form': bank_account_form})


class ProfessionalUpdate(PermissionUpdateView, generic.UpdateView):
    """
    View for Professional Update
    """
    model = Professional
    form_class = ProfessionalForm
    template_name = 'professional/professional_form2.html'
    success_url = reverse_lazy('professional:professional-list')
    queryset = Professional.objects.all()
    permission_form_fields = [{'field': 'professional_enabled', 'permission': 'can_liberate_professional'},
                              {'field': 'executive', 'permission': 'can_edit_executive'}]
    professional_document_form = modelformset_factory(ProfessionalDocument, form=ProfessionalDocumentForm,
                                                      extra=1)

    def permission_form(self, form, user):
        for permission_form_field in self.permission_form_fields:
            if not user.has_perm(permission_form_field['permission']):
                del form.fields[permission_form_field['field']]
        return form

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        executive = self.user_executive()
        if executive is not None:
            return queryset.filter(executive=executive)
        else:
            return queryset.none()

    def get_context_data(self, **kwargs):
        context = super(ProfessionalUpdate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        context['user_form'] = CustomUserForm(prefix='user_form', instance=self.object.user)
        context['address_form'] = AddressForm(prefix='address_form', instance=self.object.address)
        context['bank_account_form'] = BankAccountForm(prefix='bank_account_form', instance=self.object.bank_account)
        context['professional_document_form'] = self.professional_document_form(prefix='professional_document_form',
                                                                                queryset=ProfessionalDocument.objects.
                                                                                filter(professional_id=self.object))
        executive = self.user_executive()
        if executive is not None:
            citys = executive.get_citys.values_list('city__id', flat=True)
            context['form'].fields['cidades'].queryset = context['form'].fields['cidades'].queryset.filter(pk__in=citys)
        return context

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def get_success_url(self):
        url = '/dashboard/professional/' + str(self.object.pk) + '/category'
        return url

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object)
        form = self.permission_form(form=form, user=self.request.user)
        address_form = AddressForm(request.POST, prefix="address_form", instance=self.object.address)
        user_form = CustomUserForm(request.POST, prefix='user_form', instance=self.object.user)
        bank_account_form = BankAccountForm(request.POST, prefix='bank_account_form', instance=self.object.bank_account)
        professional_document_form = self.professional_document_form(request.POST, request.FILES, prefix='professional_document_form',
                                                                     queryset=ProfessionalDocument.objects.
                                                                                filter(professional_id=self.object))
        if form.is_valid() and address_form.is_valid() and user_form.is_valid() and bank_account_form.is_valid() and professional_document_form.is_valid():
            user = user_form.save()
            self.object = form.save(commit=False)
            address = address_form.save()
            bank_account = bank_account_form.save(commit=False)
            bank_account.save()
            self.object.bank_account = bank_account
            self.object = form.save()
            categorias = form.data.getlist('categorias')
            ProfessionalCategory.objects.filter(professional=self.object).exclude(category__in=categorias).delete()
            for category in categorias:
                ProfessionalCategory.objects.get_or_create(professional=self.object, category_id = category)
            days_of_week = form.data.getlist('days_of_week')
            ProfessionalScheduleDefault.objects.filter(professional=self.object).exclude(day_of_week__in=days_of_week).delete()
            for day in days_of_week:
                professional_sheddule_default = ProfessionalScheduleDefault.objects.filter(professional=self.object, day_of_week=day)
                if not professional_sheddule_default:
                    professional_sheddule_default = ProfessionalScheduleDefault(professional=self.object, day_of_week=day, provide_all_day=True)
                    professional_sheddule_default.save()
            badges = form.data.getlist('badges')
            ProfessionalBadge.objects.filter(professional=self.object).exclude(badge__in=badges).delete()
            for badge in badges:
                ProfessionalBadge.objects.get_or_create(professional=self.object, badge_id = badge)
            cidades = form.data.getlist('cidades')
            ProfessionalCity.objects.filter(professional=self.object).exclude(city__in=cidades).delete()
            for city in cidades:
                ProfessionalCity.objects.get_or_create(professional=self.object, city_id=city)
            pricing_criterion_professional = list(ProfessionalCategory.objects.filter(professional=self.object, category__service__pricing_criterion__isnull=False)\
                .values_list('category__service__pricing_criterion', flat=True).distinct())
            for pricing_criterion in pricing_criterion_professional:
                ProfessionalCriterion.objects.get_or_create(professional=self.object, pricing_criterion_id=pricing_criterion)
            for professional_document in professional_document_form:
                professional_document = professional_document.save(commit=False)
                professional_document.professional = self.object
                if professional_document.document_type_id is not None:
                    professional_document.save()
            return super(ProfessionalUpdate, self).form_valid(form)
        context = {'form': form, 'address_form': address_form,
                   'user_form': user_form, 'bank_account_form': bank_account_form,
                   'professional_document_form': professional_document_form}
        return render(request, self.template_name,context)


class ProfessionalResetPassword(View):
    """
    View used to reset a Professional's password using SMS
    """

    def get(self, request, *args, **kwargs):
        professional = get_object_or_404(Professional, pk=kwargs.get('pk', None))
        celphone = request.GET.get('celphone', None)
        if professional.celphone != celphone:
            professional.celphone = celphone
        sms_code = generator_code(size=6)
        sms = Sms()
        user = professional.user
        user.set_password(sms_code)
        user.save()
        msg = 'A sua senha Biuri foi atualizada. Seu usuario: ' + user.email + '  sua senha: ' + sms_code
        data = {'to': str(55) + str(celphone), 'from': 'BIURI', 'msg': msg}
        sms.send(data=data)
        professional.send_sms = True
        professional.save()
        return HttpResponse('success', status=200)



class ProfessionalTestService(View):
    """
    View used to generate a test Attendance for a given Professional(:model:`professional.Professional`)
    """

    def get(self, request, *args, **kwargs):
        professional = get_object_or_404(Professional, pk=kwargs.get('pk', None))
        self.test_service_professional(professional.pk)
        return HttpResponse('success', status=200)

    def test_service_professional(self, professional_id):
        attendance = Attendance()
        initial_service, created_service = Service.objects.get_or_create(name="Serviço Teste",
                                                                         description="Serviço para teste do aplicativo do profissional",
                                                                         category_id=1, gender="Todos",
                                                                         mean_range_time=30,
                                                                         minimal_range_price=1, is_app_enabled=False)
        attendance.initial_service = initial_service
        user, created_user = User.objects.get_or_create(first_name="Cliente Teste", last_name="Biuri",
                                                        username="contato@biuri.com.br", email="contato@biuri.com.br")
        customer, created_customer = Customer.objects.get_or_create(user=user)
        attendance.customer = customer
        professional = Professional.objects.select_related('executive__address').get(pk=professional_id)
        if professional.executive:
            address_executive = professional.executive.address
            address, created_address = UserAddress.objects.get_or_create(user=user, name="Biuri", postal_code=address_executive.postal_code,
                                                                         address=address_executive.address,
                                                                         number=address_executive.number,
                                                                         neighborhood=address_executive.neighborhood, city=address_executive.city,
                                                                         state=address_executive.state,
                                                                         latitude=-23.5401277, longitude=-46.5798907)
        else:
            address, created_address = UserAddress.objects.get_or_create(user=user, name="Biuri",
                                                                         postal_code="51021040",
                                                                         address="Av. Eng. Domingos Ferreira",
                                                                         number="4060",
                                                                         neighborhood="Boa Viagem", city="Recife",
                                                                         state="PE",
                                                                         latitude=-8.1237493, longitude=-34.9003891)
        attendance.address = address
        attendance.credit_card_id = 10
        attendance.professional_id = professional_id
        attendance.scheduling_date = datetime.datetime.now() + datetime.timedelta(days=1)
        attendance.save()
        service = AttendanceService(attendance=attendance, service=initial_service, price=1, duration=30)
        service.save()
        attendance.status = 'waiting_confirmation'
        attendance.has_evaluation = True
        attendance.has_evaluation_professional = True
        attendance.is_test = True
        attendance.save()
        return 'success'


# class Calendar(View):
#     def process_list(self,hour_blocks, hora_inicial, hora_final):
#         final_blocks = []
#         for block in hour_blocks:
#             if hora_inicial >= block[0] and hora_final <= block[1]:
#                 if block[0] != hora_inicial:
#                     final_blocks.append([block[0], hora_inicial])
#                 if block[1] != hora_final:
#                     final_blocks.append([hora_final, block[1]])
#             else:
#                 final_blocks.append([block[0], block[1]])
#         return final_blocks
#
#     def process_calendar(self,professional, date, hour_inicial, hour_final):
#         professional_sheddules = Schedule.objects.filter(professional_id=professional, daily_date=date,
#                                                          daily_time_begin__gte=hour_inicial,
#                                                          daily_time_end__lte=hour_final)
#         professional_sheddules.filter(attendance__isnull=True).delete()
#         blocks = [[hour_inicial, hour_final]]
#         for professional_sheddule in professional_sheddules:
#             hora_inicial = professional_sheddule.daily_time_begin
#             hora_final = professional_sheddule.daily_time_end
#             blocks = self.process_list(blocks, hora_inicial, hora_final)
#         for block in blocks:
#             schedule = Schedule(professional_id=professional, daily_date=date, daily_time_begin=block[0],
#                                 daily_time_end=block[1])
#             schedule.save()
#         return blocks


class Raking(View):

    def qtd_week_day(self, profissional, date_begin, date_end):
        days = Schedule.objects.filter(profissional_id=profissional, daily_date__gte=date_begin, daily_date__lt=date_end)
        days = days.values('date')
        weekday_list = []
        for day in days:
            weekday = day.weekday()
            if not weekday in weekday_list:
                weekday_list.append(weekday)
        return weekday_list

    def area_performance(self, profissional):
        cidades_profissional = ProfessionalCity.objects.filter(profissional_id=profissional)
        cidades = cidades_profissional.values_list('citys')
        total_bairros = Neighborhood.objects.filter(city__in=cidades).count()
        profissional_bairros = cidades_profissional.values_list('neighborhoods')
        return len(profissional_bairros) / total_bairros

    def services_performance(self, profissional):
        categorys_profissional = ProfessionalCategory.objects.filter(profissional_id=profissional)
        categorys = categorys_profissional.values_list('category')
        total_services = Service.objects.filter(category__in=categorys).count()
        profissional_services = categorys_profissional.values_list('services')
        return len(profissional_services) / total_services

    def evaluation(self, profissional, date_begin, date_end):
        evaluations = ProfessionalEvaluation.objects.filter(profissional_id=profissional, create__gte=date_begin, create__lt=date_end)
        average_evaluation = evaluations.aggregate(y=Avg('rating'))
        if average_evaluation['y']:
            return average_evaluation['y'] / 5
        else:
            return 0

    def attendances(self, profissional, date_begin, date_end):
        attendances = Attendance.objects.filter(status='completed', scheduling_date__gte=date_begin, scheduling_date__lt=date_end)
        total_attendances = attendances.aggregate(total=Sum('price'), count=Count('id'))
        total_attendances_professional = attendances.filter(profissional_id=profissional).aggregate(total=Sum('price'), count=Count('id'))
        if total_attendances['total'] > 0:
            participacao_qtd = total_attendances_professional['total'] / total_attendances['total']
        else:
            participacao_qtd = 0
        if total_attendances['price'] > 0:
            participacao_valor = total_attendances_professional['price'] / total_attendances['price']
        else:
            participacao_valor = 0
        return {'participacao_valor': participacao_valor, 'participacao_qtd': participacao_qtd}

    # def get_pontuality(self, profissional, date_begin, date_end):
    #     attendances = Attendance.objects.filter(status='completed', scheduling_date__gte=date_begin, scheduling_date__lt=date_end)
    #     total_attendances = attendances.aggregate(total=Sum(F('')))

    def calculate_ranking(self, profissional, date_begin, date_end):
        qtd_week_day = len(self.qtd_week_day(profissional, date_begin, date_end))
        area_performance = self.area_performance(profissional)
        services_performance = self.services_performance(profissional)
        evaluation = self.evaluation(profissional, date_begin, date_end)
        attendances = self.attendances(profissional, date_begin, date_end)
        points = 1000
        #peso weekday
        if qtd_week_day >= 5:
            points_qtd_week_day = qtd_week_day * 1
        elif qtd_week_day >= 4:
            points_qtd_week_day = qtd_week_day * 0.95
        elif qtd_week_day >= 3:
            points_qtd_week_day = qtd_week_day * 0.86
        elif qtd_week_day >= 2:
            points_qtd_week_day = qtd_week_day * 0.74
        elif qtd_week_day >= 1:
            points_qtd_week_day = qtd_week_day * 0.61
        else:
            points_qtd_week_day = 0
        points += points_qtd_week_day * 1
        points += area_performance * 1
        points += services_performance * 1
        points += evaluation * 1
        points += attendances['participacao_valor'] * 0.5 + attendances['participacao_qtd'] * 0.5
        return points


def create_image_instagram(username, sexo):
    url = get_user_information(username)['profile_pic_url_hd']
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    basewidth = 320
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)
    if sexo == 'male':
        img2 = Image.open('/Users/ytalomartins/Downloads/empreendedor_biuri.jpeg')
    else:
        img2 = Image.open('/Users/ytalomartins/Downloads/empreendedora_biuri.jpeg')
    area = (140, 140, 460, 460)
    img2.paste(img, area)
    draw = ImageDraw.Draw(img2)
    font = ImageFont.truetype("Aaargh.ttf", 16)
    draw.text((50, 50), 'TEste', (255, 255, 255), font=font)
    return img2.show()

class ExecutiveList(PermissionListView, generic.ListView):
    """
    Lists the Executives(:model:`professional.executive`)
    """
    model = Executive
    queryset = Executive.objects.all()
    template_name = 'professional/executive_list.html'


class ExecutiveCreate(PermissionCreateView, generic.CreateView):
    """
    View for Executive Creation(:model:`professional.executive`)
    """
    model = Executive
    template_name = 'professional/executive_form.html'
    form_class = ExecutiveForm
    success_url = reverse_lazy('professional:executive-list')

    def get_context_data(self, **kwargs):
        context = super(ExecutiveCreate, self).get_context_data(**kwargs)
        context['user_form'] = CustomUserForm(prefix='user_form')
        context['address_form'] = AddressForm(prefix='address_form')
        context['bank_account_form'] = BankAccountForm(prefix='bank_account_form')
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, request.FILES)
        address_form = AddressForm(request.POST, prefix="address_form")
        user_form = CustomUserForm(request.POST, prefix='user_form')
        bank_account_form = BankAccountForm(request.POST, prefix='bank_account_form')

        if form.is_valid() and address_form.is_valid() and user_form.is_valid() and bank_account_form.is_valid():
            user = user_form.save()
            self.object = form.save(commit=False)
            self.object.user = user
            address = address_form.save(commit=False)
            address.save()
            bank_account = bank_account_form.save(commit=False)
            bank_account.save()
            self.object.address = address
            self.object.bank_account = bank_account
            self.object = form.save()
            city_executive_models = []
            for city in form.data.getlist('cidades'):
                city_executive = ExecutiveCity(executive=self.object, city_id=city)
                city_executive_models.append(city_executive)
            ExecutiveCity.objects.bulk_create(city_executive_models)
            return super(ExecutiveCreate, self).form_valid(form)
        return render(request, self.template_name, {'form': form, 'address_form': address_form, 'user_form': user_form,
                                                    'bank_account_form': bank_account_form})


class ExecutiveUpdate(PermissionUpdateView, generic.UpdateView):
    """
    View for Executive Update(:model:`professional.executive`)
    """
    model = Executive
    form_class = ExecutiveForm
    template_name = 'professional/executive_form.html'
    success_url = reverse_lazy('professional:executive-list')
    queryset = Executive.objects.all()

    def get_context_data(self, **kwargs):
        context = super(ExecutiveUpdate, self).get_context_data(**kwargs)
        context['user_form'] = CustomUserForm(prefix='user_form', instance=self.object.user)
        context['address_form'] = AddressForm(prefix='address_form', instance=self.object.address)
        context['bank_account_form'] = BankAccountForm(prefix='bank_account_form', instance=self.object.bank_account)
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, request.FILES, instance=self.object)
        address_form = AddressForm(request.POST, prefix="address_form", instance=self.object.address)
        user_form = CustomUserForm(request.POST, prefix='user_form', instance=self.object.user)
        bank_account_form = BankAccountForm(request.POST, prefix='bank_account_form', instance=self.object.bank_account)

        if form.is_valid() and address_form.is_valid() and user_form.is_valid() and bank_account_form.is_valid():
            user = user_form.save()
            self.object = form.save(commit=False)
            address = address_form.save()
            bank_account = bank_account_form.save(commit=False)
            bank_account.save()
            self.object.address = address
            self.object.bank_account = bank_account
            self.object = form.save()
            cidades = form.data.getlist('cidades')
            ExecutiveCity.objects.filter(executive=self.object).exclude(city__in=cidades).delete()
            for city in cidades:
                ExecutiveCity.objects.get_or_create(executive=self.object, city_id=city)
            return super(ExecutiveUpdate, self).form_valid(form)
        context = {'form': form, 'address_form': address_form, 'user_form': user_form, 'bank_account_form': bank_account_form}
        return render(request, self.template_name, context)


class SellerList(PermissionListView, TypeUserMixin, GenericFilterList):
    """
    Lists the Sellers(:model:`professional.seller`)
    """
    ordering = 'id'
    model = Seller
    template_name = 'professional/seller_list.html'
    filterset_class = GenericFilter
    verbose_name = 'Vendedor'
    verbose_name_plural = 'Vendedores'
    add_display_name = 'Adicionar Vendedor'
    queryset = Seller.objects.select_related('user')
    ordering = ['user__first_name']
    # list_display = ['id', 'rating', 'user__first_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        executive = self.user_executive()
        if executive is not None:
            return queryset.filter(executive=executive)
        else:
            return queryset.none()

    def get_context_data(self, **kwargs):
        context = super(SellerList, self).get_context_data(**kwargs)
        context['seller'] = Professional.objects.filter(user=self.request.user)
        return context


class SellerCreate(PermissionCreateView, TypeUserMixin, generic.CreateView):
    """
    View for Seller Creation(:model:`professional.seller`)
    """
    model = Seller
    template_name = 'professional/seller_form.html'
    form_class = SellerForm
    success_url = reverse_lazy('professional:seller-list')
    permission_form_fields = [{'field': 'executive', 'permission': 'can_edit_executive'}]

    def permission_form(self, form, user):
        for permission_form_field in self.permission_form_fields:
            if not user.has_perm(permission_form_field['permission']):
                del form.fields[permission_form_field['field']]
        return form

    def get_context_data(self, **kwargs):
        context = super(SellerCreate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        context['user_form'] = CustomUserForm(prefix='user_form')
        context['address_form'] = AddressForm(prefix='address_form')
        context['bank_account_form'] = BankAccountForm(prefix='bank_account_form')
        executive = self.user_executive()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        form = self.permission_form(form=form, user=self.request.user)
        address_form = AddressForm(request.POST, prefix="address_form")
        user_form = CustomUserForm(request.POST, prefix='user_form')
        bank_account_form = BankAccountForm(request.POST, prefix='bank_account_form')

        if form.is_valid() and address_form.is_valid() and user_form.is_valid() and bank_account_form.is_valid():
            user = user_form.save()
            self.object = form.save(commit=False)
            self.object.user = user
            address = address_form.save(commit=False)
            address.save()
            bank_account = bank_account_form.save(commit=False)
            bank_account.save()
            self.object.address = address
            self.object.bank_account = bank_account
            executive = self.user_executive()
            if executive is not None:
                self.object.executive = executive
            self.object = form.save()
            return super(SellerCreate, self).form_valid(form)
        return render(request, self.template_name, {'form': form, 'address_form': address_form, 'user_form': user_form,
                                                    'bank_account_form': bank_account_form})


class SellerUpdate(PermissionUpdateView, TypeUserMixin, generic.UpdateView):
    """
    View for Seller Update(:model:`professional.seller`)
    """
    model = Seller
    template_name = 'professional/seller_form.html'
    form_class = SellerForm
    success_url = reverse_lazy('professional:seller-list')
    permission_form_fields = [{'field': 'executive', 'permission': 'professional.can_edit_executive'}]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        executive = self.user_executive()
        if executive is not None:
            return queryset.filter(executive=executive)
        else:
            return queryset.none()

    def permission_form(self, form, user):
        for permission_form_field in self.permission_form_fields:
            if not user.has_perm(permission_form_field['permission']):
                del form.fields[permission_form_field['field']]
        return form

    def get_context_data(self, **kwargs):
        context = super(SellerUpdate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        context['user_form'] = CustomUserForm(prefix='user_form', instance=self.object.user)
        context['address_form'] = AddressForm(prefix='address_form',  instance=self.object.address)
        context['bank_account_form'] = BankAccountForm(prefix='bank_account_form',  instance=self.object.bank_account)
        executive = self.user_executive()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        form = self.permission_form(form=form, user=self.request.user)
        address_form = AddressForm(request.POST, prefix="address_form", instance=self.object.address)
        user_form = CustomUserForm(request.POST, prefix='user_form', instance=self.object.user)
        bank_account_form = BankAccountForm(request.POST, prefix='bank_account_form', instance=self.object.bank_account)

        if form.is_valid() and address_form.is_valid() and user_form.is_valid() and bank_account_form.is_valid():
            user = user_form.save()
            self.object = form.save(commit=False)
            self.object.user = user
            address = address_form.save(commit=False)
            address.save()
            bank_account = bank_account_form.save(commit=False)
            bank_account.save()
            self.object.address = address
            self.object.bank_account = bank_account
            self.object = form.save()
            return super(SellerUpdate, self).form_valid(form)
        return render(request, self.template_name, {'form': form, 'address_form': address_form, 'user_form': user_form,
                                                    'bank_account_form': bank_account_form})

class PdfTerms(View):
    """
    View that generates a printable PDF with the Professional's register information
    """

    def get(self, request, *args, **kwargs):
        query_params = self.request.GET.dict()
        professional = get_object_or_404(Professional.objects.select_related('user', 'address', 'executive__user', 'bank_account'), pk=kwargs.get('pk', None))
        service_professional = ServiceProfessional.objects.select_related('service').filter(professional=professional).order_by('service__category__name', 'service__name', 'service__gender')
        schedule = ProfessionalScheduleDefault.objects.filter(professional=professional).order_by('day_of_week')
        citys = ProfessionalCity.objects.select_related('city').prefetch_related('neighborhoods').filter(professional=professional)
        services_list = []
        attendance_percent = professional.attendance_percent / 100
        for service in service_professional:
            if service.service.pricing_criterion:
                options = ServiceProfessionalPricingCriterion.objects.select_related('pricingcriterionoptions').filter(service_professional=service)
                for option in options:
                    services_list.append({'name': service.service.name + " - " + option.pricingcriterionoptions.description , 'gender': service.service.gender, 'minimum_price': option.price, 'average_time': service.average_time,
                                  'maximum_price': option.price, 'maximum_received': float(option.price)*attendance_percent,
                                  'minimum_received': float(option.price)*attendance_percent})
            else:
                services_list.append({'name': service.service.name, 'gender': service.service.gender, 'minimum_price': service.minimum_price, 'average_time': service.average_time,
                                  'maximum_price': service.maximum_price, 'maximum_received': float(service.maximum_price)*attendance_percent,
                                  'minimum_received': float(service.minimum_price)*attendance_percent})
        params = {
            'request': request,
            'os': '',
            'professional': professional,
            'service_professional': services_list,
            'schedule': schedule,
            'citys': citys,
        }
        full_name = normalize('NFKD', professional.full_name).encode('ASCII', 'ignore').decode('ASCII')
        return render_pdf_view(request=request, template_path='professional/professional_terms.html', context=dict(params), filename='Termo de Veracidade - ' + full_name)

class PdfContract(View):
    """
    View that generates a printable contract for the Professional
    """

    def get(self, request, *args, **kwargs):
        query_params = self.request.GET.dict()
        professional = get_object_or_404(Professional.objects.select_related('user', 'address', 'executive__user', 'bank_account'), pk=kwargs.get('pk', None))
        contract = Contract.objects.filter(id=1)
        clauses = ContractClause.objects.filter(contract=contract)
        clause_list = []
        for clause in clauses:
            t = Template('<h2>' + clause.text + '</h2>')
            c = Context({'professional': professional})
            html = t.render(c)
            clause_list.append({'message': html})
        params = {
            'request': request,
            'os': '',
            'professional': professional,
            'contract': contract,
            'clause_list': clause_list,
        }
        return render_pdf_view(request=request, template_path='professional/professional_contract.html', context=dict(params), filename='Termo de Veracidade - ' + professional.full_name)

def test_service_professional(professional_id):
    attendance = Attendance()
    initial_service, created_service = Service.objects.get_or_create(name="Serviço Teste",
                                                    description="Serviço para teste do aplicativo do profissional",
                                                    category_id=1, gender="Todos", mean_range_time=30,
                                                    minimal_range_price=1, is_app_enabled=False)
    attendance.initial_service = initial_service
    user, created_user = User.objects.get_or_create(first_name="Cliente Teste", last_name="Biuri",
                                                    username="contato@biuri.com.br", email="contato@biuri.com.br")
    customer, created_customer = Customer.objects.get_or_create(user=user)
    attendance.customer = customer
    address, created_address = UserAddress.objects.get_or_create(user=user, name="Biuri", postal_code="51021040",
                                     address="Av. Eng. Domingos Ferreira", number="4060",
                                     neighborhood="Boa Viagem", city="Recife", state="PE",
                                     latitude=-8.1237493, longitude=-34.9003891)
    attendance.address = address
    attendance.credit_card_id = 210
    attendance.professional_id = professional_id
    attendance.scheduling_date = datetime.datetime.now() + datetime.timedelta(days=1)
    attendance.save()
    service = AttendanceService(attendance=attendance, service=initial_service, price=1, duration=30)
    service.save()
    attendance.status = 'waiting_confirmation'
    attendance.has_evaluation = True
    attendance.has_evaluation_professional = True
    attendance.is_test = True
    attendance.save()
    return 'success'


class MessagePushList(generic.ListView):
    """
    Lists the Push Messages(:model:`message_core.PushSchedule`)
    """
    model = PushSchedule
    queryset = PushSchedule.objects.order_by('-date_schedule')
    template_name = 'message/message_list.html'

    # def get_queryset(self):
    #     queryset = super().get_queryset()
    #     executive = self.user_executive()
    #     if self.request.user.is_superuser:
    #         return queryset
    #     if executive is not None:
    #         return queryset.filter(executive=executive)
    #     else:
    #         return queryset.none()

class MessageCreate(generic.CreateView):
    """
    View for Push Message(:model:`message_core.PushSchedule`) creation
    """
    model = PushSchedule
    template_name = 'message/message_form.html'
    form_class = PushScheduleForm
    success_url = '/dashboard/message/push'
    # queryset = PushSchedule.objects.all()

    def get_success_url(self):
        if self.object.send_region:
            return '/dashboard/message/push/' + str(self.object.pk) + '/update_region'
        return self.success_url

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            self.object = form.save()
            city_push_models = []
            for city in form.data.getlist('cidades'):
                city_professional = PushScheduleCity(push_schedule=self.object, city_id=city)
                city_push_models.append(city_professional)
            PushScheduleCity.objects.bulk_create(city_push_models)
            return super(MessageCreate, self).form_valid(form)
        return super(MessageCreate, self).form_invalid(form)


class MessageUpdate(generic.UpdateView):
    """
    View for Push Message(:model:`message_core.PushSchedule`) update
    """
    model = PushSchedule
    template_name = 'message/message_form.html'
    form_class = PushScheduleForm
    success_url = '/dashboard/message/push'

    def get_success_url(self):
        if self.get_object().send_region:
            return '/dashboard/message/push/' + str(self.get_object().pk) + '/update_region'
        return self.success_url

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.get_object())
        if form.is_valid():
            PushScheduleCity.objects.exclude(city__in=form.data.getlist('cidades')).delete()
            for city in form.data.getlist('cidades'):
                PushScheduleCity.objects.get_or_create(push_schedule=self.get_object(), city_id=city)
            return super(MessageUpdate, self).form_valid(form)

class MessageUpdateRegion(View):
    """
    View used the change the target City(:model:`message_core.PushScheduleCity`) of a given Push Message(:model:`message_core.PushSchedule`)
    """
    model = PushScheduleCity
    template_name = 'message/message_city_form.html'
    cityprofessional = modelformset_factory(PushScheduleCity,
                                               form=ProfessionalCityForm, can_delete=False,
                                               exclude=['push_schedule'], extra=0)
    def get(self, request, *args, **kwargs):
        context={}
        pk = kwargs.get('pk', None)
        formset = self.cityprofessional(queryset=PushScheduleCity.objects.select_related('city').prefetch_related('neighborhoods').filter(push_schedule_id=pk))
        context['form'] = formset
        return render(request,self.template_name,context)

    def post(self, request, *args, **kwargs):
        context={}
        formset = self.cityprofessional(request.POST)
        context['form'] = formset
        if formset.is_valid():
            formset.save()
            return redirect('/dashboard/message/push')
        return render(request,self.template_name,context)


def delete_picture(request):
    """
    Deletes selected Professional Picture(:model:`professional.ProfessionalPicture`)
    """
    name = request.POST.get('name', None)
    picture = ProfessionalPicture.objects.get(picture=name)
    print(picture.picture)
    picture.delete()
    return 'success'

def newest_picture(request):
    """
    Returns the newest Professional Picture(:model:`professional.ProfessionalPicture`)
    """
    pk = request.GET.get('pk', None)
    queryset = ProfessionalPicture.objects.filter(professional_id=pk).order_by('-id')
    picture = queryset[0]
    data = {
        'picture': picture.picture.name,
        'url': picture.picture.url,
        'size': picture.picture.size,
    }
    return JsonResponse(data)