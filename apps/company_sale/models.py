from decimal import Decimal

from django.db import models

from django.contrib.auth.models import User
from django.db.models import Sum, F, DecimalField
from django.db.transaction import atomic
from django.utils.text import slugify

from apps.common.models import BestPraticesModel
from apps.common.models import Address
from django.core.validators import MaxValueValidator, MinValueValidator
from apps.iugu.token import Token
from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from django.utils.crypto import get_random_string

from apps.iugu.models import IuguCustomerCompanyAccount, IuguInvoice
from apps.payment.models import Voucher

from apps.service_core.models import Service

class Bundle(BestPraticesModel):
    """
    Model for a Bundle
    """
    name = models.TextField(max_length=200, null=True, blank=True, verbose_name='Pacote')
    description = models.TextField(max_length=500, null=True, blank=True, verbose_name='Descrição do pacote')
    observation = models.TextField(max_length=500, null=True, blank=True, verbose_name='Observações sobre o pacote')

    class Meta:
        verbose_name = "Pacote"
        # permissions = (('can_create_bundle','Poder criar um pacote'),
        #                ('can_edit_bundle','Pode editar o pacote'))

    def __str__(self):
        return '{}'.format(self.id)


class BundleService(BestPraticesModel):
    """
    Stores the Services(:model:`service_core.service`) of a Bundle(:model:`company_sale.bundle`)
    """
    bundle = models.ForeignKey(Bundle, related_name='bundle', verbose_name='Pacote')
    service = models.ForeignKey('service_core.Service', related_name='service', verbose_name='Serviço')
    quantity = models.PositiveIntegerField(verbose_name="Quantidade", default=0, blank=True)
    price = models.DecimalField(verbose_name="Preço", max_digits=12, decimal_places=2, default=0, blank=True)

    class Meta:
        verbose_name = "Pacote Serviço"

    def __str__(self):
        return '{}'.format(self.id)


class Company(BestPraticesModel, IuguCustomerCompanyAccount):
    """
    Model for Companies
    """
    cnpj = models.CharField(max_length=14, verbose_name='CNPJ', unique=True)
    state_registration = models.CharField(max_length=12, null=True, blank=True, verbose_name='Inscrição Estadual')
    company_name = models.CharField(max_length=30, verbose_name='Razão Social')
    trading_name = models.CharField(max_length=30, verbose_name='Nome Fantasia')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)
    phone = models.CharField(max_length=11, null=True, blank=True, verbose_name='Telefone')
    email = models.CharField(max_length=30, verbose_name='E-mail', unique=True)
    contact_name = models.CharField(max_length=30, verbose_name='Contato na Empresa')
    contact_cellphone = models.CharField(max_length=11, null=True, blank=True, verbose_name='Telefone do Contato')
    contact_email = models.CharField(max_length=30, null =True, blank=True, verbose_name='E-mail do Contato')
    customer = models.ForeignKey('customer.Customer', null=True, blank=True, related_name='customer', verbose_name='Cliente')
    observation = models.TextField(max_length=500, null=True, blank=True, verbose_name='Observações')

    class Meta:
        verbose_name = "Company"
        permissions = (('list_company', 'Can view list of companies'),
                       )

    def __str__(self):
        return '{} - {}'.format(self.cnpj,self.trading_name)


class VoucherSale(BestPraticesModel):
    """
    Stores the Vouchers(:model:`payment.voucher`) of a Sale(:model:`company_sale.sale`)
    """
    sale = models.ForeignKey('Sale', verbose_name='Venda')
    voucher = models.ForeignKey(Voucher)


class SaleVoucherGenerator(BestPraticesModel):
    """
    Generates Vouchers for a Company Sale
    """
    service = models.ForeignKey(Service, verbose_name='Serviço', related_name='service_voucher', null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Quantidade", default=0, blank=True)
    value = models.DecimalField(verbose_name="Valor", max_digits=12, decimal_places=2, default=0, blank=True)
    observation = models.TextField(max_length=100, null=True, blank=True, verbose_name='Observações')
    sale = models.ForeignKey('Sale', related_name='sale_generator', verbose_name='Venda', blank=True, null=True)
    initial_date = models.DateTimeField(verbose_name='Data inicial')
    final_date = models.DateTimeField(verbose_name='Data final')

    def __str__(self):
        return '{}'.format(self.service)


class Sale(BestPraticesModel, IuguInvoice):
    STATUS = Choices('draft', 'negotiating', 'waiting_approval', 'waiting_payment', 'completed', 'canceled')
    company = models.ForeignKey(Company, related_name='company', verbose_name='Empresa')
    seller = models.ForeignKey('professional.seller', related_name='seller', verbose_name='Vendedor', null=True, blank=True)
    executive = models.ForeignKey('professional.executive', related_name='sale_executive', verbose_name='Executivo', null=True, blank=True)
    commission = models.PositiveIntegerField(default=10, validators=[MaxValueValidator(25), MinValueValidator(0)],
                                             verbose_name='Comissão')
    observation = models.TextField(max_length=500, null=True, blank=True, verbose_name='Observações sobre a venda')
    status = StatusField(choices_name='STATUS', default=STATUS.draft, db_index=True)
    price = models.DecimalField(verbose_name="Preço", max_digits=12, decimal_places=2, default=0, blank=True)
    bundle = models.ForeignKey(Bundle, related_name='sale_bundle', verbose_name='Pacote', null=True)
    waiting_approval_date = MonitorField(monitor='status', when=['waiting_approval'], null=True, blank=True,
                                         default=None)
    waiting_payment_date = MonitorField(monitor='status', when=['waiting_payment'], null=True, blank=True, default=None)
    completed_date = MonitorField(monitor='status', when=['completed'], null=True, blank=True, default=None)
    canceled_date = MonitorField(monitor='status', when=['canceled'], null=True, blank=True, default=None)

    class Meta:
        verbose_name = "Sale"
        permissions = (('list_sale', 'Can view list of sales'),
                       ('edit_sale_seller', 'Can edit seller on Sale'),
                       ('edit_sale_executive', 'Can edit executive on Sale'))

    def __str__(self):
        return '{}'.format(self.id)

    @atomic
    def generate_vouchers(self):
        items = SaleVoucherGenerator.objects.select_related('service').filter(sale=self)
        vouchers = []
        part_code = get_random_string(length=6, allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ0123456789')
        for item in items:
            list_voucher = list(range(1,item.quantity + 1))
            for voucher in list_voucher:
                voucher = Voucher(discount_type='value', discount_value=item.value,
                                        initial_date=item.initial_date, final_date=item.final_date,
                                        service=item.service,
                                        code=part_code + get_random_string(length=6,
                                                                           allowed_chars='ABCDEFGHJKLMNPQRSTUVWXYZ0123456789'),
                                        observation='Observações da venda: {}\nVendido para: {}\n Cupom: {} de {}'
                                       .format(self.observation, self.company, voucher, item.quantity))
                voucher.save()
                VoucherSale.objects.create(sale=self, voucher=voucher)
        return vouchers

    def charge(self):
        items = SaleVoucherGenerator.objects.select_related('service').filter(sale=self)
        items_list = []
        for item in items:
            service = ''
            if item.service:
                service = "Cupom para " + item.service.name
            else:
                service = "Cupom para todos os serviços"
            items_list.append({'description': service, 'quantity': item.quantity, 'price_cents': int(item.value*100)})
        data = {
            'method': 'bank_slip',
            'customer_id': self.company.iugu_client_id,
            'email': self.company.email,
            'items': items_list,
            'restrict_payment_method': True,
            'order_id': str(self.id)
        }
        token = Token().charge(data)
        # self.update_data_iugu(data=token)
        return token

    def change_status(self, atual_status, new_status):
        if atual_status == 'waiting_approval' and new_status == 'waiting_payment':
            return self.charge()
        if atual_status == 'waiting_payment' and new_status == 'completed':
            self.generate_vouchers()
        return {}

    def update_total_price(self):
        queryset = SaleVoucherGenerator.objects.filter(sale=self).aggregate(y=Sum(F('value') * F('quantity'),
                                                                       output_field=DecimalField()))
        print(queryset)
        if 'y' in queryset:
            if queryset['y'] is not None:
                return queryset['y']
        return 0

    def save(self, *args, **kwargs):
        if self.pk:
            old_sale = Sale.objects.get(pk=self.pk)
            data = self.change_status(atual_status=old_sale.status, new_status=self.status)
            if 'invoice_id' in data:
                self.invoice_id = data['invoice_id']
                self.information_data = data
            self.price = self.update_total_price()
        return super(Sale, self).save(*args, **kwargs)
