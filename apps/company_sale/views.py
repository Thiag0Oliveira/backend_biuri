from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Avg, Count, F, Sum
from django.forms.models import inlineformset_factory, modelformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from oauth2_provider.models import AccessToken

from django.views import View
from io import BytesIO
from django.template import Context, Template
import os
import requests


from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa


from apps.core.forms import AddressForm, CustomUserForm
from apps.common.views import GenericFilterList, PermissionListView, PermissionUpdateView, PermissionCreateView, render_pdf_view
from apps.payment.models import Voucher
from apps.professional.filters import GenericFilter
from apps.professional.mixins import TypeUserMixin

from .forms import (
    CompanyForm, SaleForm, SaleVoucherGeneratorForm
)

from .models import (
    Company, Sale, SaleVoucherGenerator,
    VoucherSale)

from apps.professional.models import (
    Executive, Seller
)


class CompanyList(PermissionListView, GenericFilterList):
    """
    Lists customer Companies(:model:`company_sale.Company`)
    """
    ordering = 'id'
    model = Company
    template_name = 'company/company_list.html'
    filterset_class = GenericFilter
    verbose_name = 'Empresa'
    verbose_name_plural = 'Clientes PJ'
    add_display_name = 'Adicionar Empresa'
    queryset = Company.objects.select_related('user')
    ordering = ['user__first_name']

    def get_context_data(self, **kwargs):
        context = super(CompanyList, self).get_context_data(**kwargs)
        context['company'] = Company.objects.filter(user=self.request.user)
        return context


class CompanyCreate(PermissionCreateView, generic.CreateView):
    """
    View for customer Company(:mode:`company_sale.Company`) creation
    """
    model = Company
    template_name = 'company/company_form.html'
    form_class = CompanyForm
    success_url = reverse_lazy('company:company-list')
    permission_form_fields = [{'field': 'company', 'permission': 'can_edit_company'}]

    def permission_form(self, form, user):
        # for permission_form_field in self.permission_form_fields:
        #     if not user.has_perm(permission_form_field['permission']):
        #         del form.fields[permission_form_field['field']]
        return form

    def get_context_data(self, **kwargs):
        context = super(CompanyCreate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        context['user_form'] = CustomUserForm(prefix='user_form')
        context['address_form'] = AddressForm(prefix='address_form')
        executive = self.user_executive()
        return context

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        form = self.permission_form(form=form, user=self.request.user)
        address_form = AddressForm(request.POST, prefix="address_form")
        user_form = CustomUserForm(request.POST, prefix='user_form')

        if form.is_valid() and address_form.is_valid() and user_form.is_valid():
            user = user_form.save()
            self.object = form.save(commit=False)
            self.object.user = user
            address = address_form.save(commit=False)
            address.save()
            self.object.address = address
            executive = Executive.objects.filter(user=request.user)
            if executive:
                executive = executive[0]
                self.object.executive = executive
            self.object = form.save()
            return super(CompanyCreate, self).form_valid(form)
        return render(request, self.template_name, {'form': form, 'address_form': address_form, 'user_form': user_form})


class CompanyUpdate(PermissionUpdateView, TypeUserMixin, generic.UpdateView):
    """
    View for customer Company(:mode:`company_sale.Company`) update
    """
    model = Company
    template_name = 'company/company_form.html'
    form_class = CompanyForm
    success_url = reverse_lazy('company:company-list')
    permission_form_fields = [{'field': 'company', 'permission': 'can_edit_company'}]
    queryset = Company.objects.all()

    def permission_form(self, form, user):
        # for permission_form_field in self.permission_form_fields:
        #     if not user.has_perm(permission_form_field['permission']):
        #         del form.fields[permission_form_field['field']]
        return form

    def get_context_data(self, **kwargs):
        context = super(CompanyUpdate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        context['user_form'] = CustomUserForm(prefix='user_form', instance=self.object.user)
        context['address_form'] = AddressForm(prefix='address_form',  instance=self.object.address)
        executive = self.user_executive()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        form = self.permission_form(form=form, user=self.request.user)
        address_form = AddressForm(request.POST, prefix="address_form", instance=self.object.address)
        user_form = CustomUserForm(request.POST, prefix='user_form', instance=self.object.user)

        if form.is_valid() and address_form.is_valid() and user_form.is_valid():
            user = user_form.save()
            self.object = form.save(commit=False)
            self.object.user = user
            address = address_form.save(commit=False)
            address.save()
            self.object.address = address
            self.object = form.save()
            return super(CompanyUpdate, self).form_valid(form)
        return render(request, self.template_name, {'form': form, 'address_form': address_form, 'user_form': user_form})


class SaleList(PermissionListView, TypeUserMixin, GenericFilterList):
    """
    Lists Sales(:model:`company_sale.Sale`)
    """
    ordering = 'id'
    model = Sale
    template_name = 'company/sale_list.html'
    filterset_class = GenericFilter
    verbose_name = 'Vendas'
    verbose_name_plural = 'Vendas'
    add_display_name = 'Criar nova venda'
    queryset = Sale.objects.all()
    ordering = '-id'

    # list_display = ['id', 'rating', 'user__first_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        executive = self.user_executive()
        if executive is not None:
            return queryset.filter(executive=executive)
        seller = self.user_seller()
        if seller is not None:
            return queryset.filter(seller=seller)
        else:
            return queryset.none()

    def get_context_data(self, **kwargs):
        context = super(SaleList, self).get_context_data(**kwargs)
        return context


class SaleCreate(PermissionCreateView, TypeUserMixin, generic.CreateView):
    """
    View for Sales(:model:`company_sale.Sale`) creation
    """
    model = Sale
    template_name = 'company/sale_create_form.html'
    form_class = SaleForm
    permission_form_fields = [{'field': 'commission', 'permission': 'professional.can_edit_seller'},
                              {'field': 'seller', 'permission': 'professional.can_edit_seller'}]

    def permission_form(self, form, user):
        for permission_form_field in self.permission_form_fields:
            if not user.has_perm(permission_form_field['permission']):
                del form.fields[permission_form_field['field']]
        return form

    def get_success_url(self):
        url = '/dashboard/company/sale/' + str(self.object.pk) + '/edit'
        return url

    def get_context_data(self, **kwargs):
        context = super(SaleCreate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        executive = self.user_executive()
        seller = self.user_seller()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        form = self.permission_form(form=form, user=self.request.user)

        if form.is_valid():
            self.object = form.save(commit=False)
            executive = self.user_executive()
            if executive is not None:
                self.object.executive = executive
            seller = self.user_seller()
            if seller is not None:
                self.object.seller = seller
                self.object.executive = seller.executive
            self.object = form.save()
            return super(SaleCreate, self).form_valid(form)
        return render(request, self.template_name, {'form': form})


class SaleUpdate(PermissionUpdateView, TypeUserMixin, generic.UpdateView):
    """
    View for Sales(:model:`company_sale.Sale`) update
    """
    model = Sale
    template_name = 'company/sale_form.html'
    form_class = SaleForm
    success_url = reverse_lazy('company:sale-list')
    permission_form_fields = [{'field': 'seller', 'permission': 'company_sale.edit_sale_seller'},
                              {'field': 'company', 'permission': 'company_sale.edit_sale_company'},
                              {'field': 'executive', 'permission': 'company_sale.edit_sale_executive'},
                              {'field': 'commission', 'permission': 'company_sale.edit_sale_seller'}]
    # queryset = Sale.objects.all()
    sale_voucher_generator_form = modelformset_factory(SaleVoucherGenerator, form=SaleVoucherGeneratorForm,
                                                       extra=1, can_delete=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        executive = self.user_executive()
        if executive is not None:
            return queryset.filter(executive=executive)
        seller = self.user_seller()
        if seller is not None:
            return queryset.filter(seller=seller)
        else:
            return queryset.none()

    def permission_form(self, form, user):
        for permission_form_field in self.permission_form_fields:
            if not user.has_perm(permission_form_field['permission']):
                del form.fields[permission_form_field['field']]
        return form

    def get_context_data(self, **kwargs):
        context = super(SaleUpdate, self).get_context_data(**kwargs)
        context['form'] = self.permission_form(form=context['form'], user=self.request.user)
        queryset_voucher = SaleVoucherGenerator.objects.filter(sale=self.object)
        if queryset_voucher.count() > 0:
            self.sale_voucher_generator_form.extra = 0
        sale_voucher_generator_form = self.sale_voucher_generator_form(prefix='sale_voucher_generator_form',
                                         queryset=SaleVoucherGenerator.objects.
                                         filter(sale=self.object))
        context['sale_voucher_generator_form'] = sale_voucher_generator_form
        executive = self.user_executive()
        return context

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.form_class(request.POST, instance=self.object)
        form = self.permission_form(form=form, user=self.request.user)
        sale_voucher_generator_form = self.sale_voucher_generator_form(request.POST, prefix='sale_voucher_generator_form',
                                                                       queryset=SaleVoucherGenerator.objects.
                                                                       filter(sale_id=self.object))
        if form.is_valid() and sale_voucher_generator_form.is_valid():
            self.object = form.save()
            sale_voucher_generator = sale_voucher_generator_form.save(commit=False)
            for sale_voucher_generator_form_item in sale_voucher_generator:
                sale_voucher_generator_form_item.sale = self.object
                sale_voucher_generator_form_item.save()
            for obj in sale_voucher_generator_form.deleted_objects:
                obj.delete()
            self.object = form.save()
            return super(SaleUpdate, self).form_valid(form)
        return render(request, self.template_name, {'form': form, 'sale_voucher_generator_form': sale_voucher_generator_form})



def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path

def extract_request_variables(request):

    page_size = request.POST.get('page_size', 'letter')
    page_orientation = request.POST.get('page_orientation', 'portrait')

    pagesize = "%s %s" % (
        page_size, page_orientation
    )

    template = Template(request.POST.get('data', ''))
    data = template.render(Context({}))
    return {
        'pagesize': pagesize,
        'data': data,
        'page_orientation': page_orientation,
        'page_size': page_size,
        'example_number': request.POST.get("example_number", '1'),
        'border': request.POST.get('border', '')
    }


# Create your views here.
def render_pdf(request, template_path, context, download=False):

    context = extract_request_variables(request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = ''
    if download:
        response['Content-Disposition'] = 'attachment; '
    response['Content-Disposition'] += 'filename="report.pdf"'

    template = get_template(template_path)
    html = template.render(context=context)
    if request.GET.get('show_html', ''):
        response['Content-Type'] = 'application/text'
        response['Content-Disposition'] = 'attachment; filename="report.txt"'
        response.write(html)
    else:
        pisaStatus = pisa.CreatePDF(
            html, dest=response, link_callback=link_callback)
        if pisaStatus.err:
            return HttpResponse('We had some errors with code %s <pre>%s</pre>' % (pisaStatus.err,
                                                                                   html))
    return response

def render_pdf_view(request, template_path, context):
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="report.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context=context)

    # create a pdf
    pisaStatus = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisaStatus.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


class Render:

    @staticmethod
    def render(path: str, params: dict):
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type='application/pdf')
        else:
            return HttpResponse("Error Rendering PDF", status=400)

class Pdf(View):
    """
    Generates a PDF file for a single Voucher
    """

    def get(self, request, *args, **kwargs):
        query_params = self.request.GET.dict()
        voucher = self.kwargs.get('voucher')
        voucher = get_object_or_404(Voucher, pk=voucher)
        params = {
            'request': request,
            'os': '',
            'voucher': voucher,
        }
        return render_pdf_view(request=request, template_path='payment/pdf_voucher.html', context=params)


class PdfSale(View):
    """
    Generates a PDF file for multiple Vouchers
    """

    def get(self, request, *args, **kwargs):
        query_params = self.request.GET.dict()
        sale = self.kwargs.get('sale')
        vouchers = VoucherSale.objects.select_related('voucher', 'voucher__service').filter(sale_id=int(sale))
        params = {
            'request': request,
            'os': '',
            'vouchers': vouchers,
        }
        return render_pdf_view(request=request, template_path='payment/sale_voucher.html', context=dict(params))

def get_address(cep):
    request = requests.get(
        'http://www.cepaberto.com/api/v3/cep?cep=' + cep,
        headers={'Authorization': 'Token token=055cc8e8b0e25d6b6bb30a6dad8b1932'})
    response = request.json()
    response['cidade'] = response['cidade']['nome']
    response['estado'] = response['estado']['sigla']
    response['logradouro'] = response['logradouro'].split(',')[0]
    return JsonResponse(response, status=request.status_code)


class GetCompany(View):
    """
    Gets Company data using CNPJ from https://www.receitaws.com.br/v1/cnpj/
    """
    def get(self, request, *args, **kwargs):
        url = 'https://www.receitaws.com.br/v1/cnpj/' + self.kwargs['pk']
        request = requests.get(url)
        response = request.json()
        return JsonResponse(response, status=request.status_code)
