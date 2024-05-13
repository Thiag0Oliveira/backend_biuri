from django.db import models
from django.utils.translation import ugettext_lazy as _
from datetime import datetime

from model_utils import Choices
from model_utils.models import StatusField

from apps.common.fields import JSONField
from apps.common.models import BestPraticesModel
from apps.common.views import slug_generator
from apps.customer.models import Customer

from apps.professional.models import Executive


BANCOS = [
    ('Banco do Brasil', '001 - BANCO DO BRASIL S.A.'),
    ('Santander', '033 - BANCO SANTANDER (BRASIL) S.A.'),
    ('Bradesco', '036 - BANCO BRADESCO BBI S.A.'),
    ('Caixa Econômica', '104 - CAIXA ECONOMICA FEDERAL'),
    ('Itaú', '041 - BANCO ITAÚ S.A.'),
    ('Sicredi', '748 - BANCO COOPERATIVO SICREDI S.A.'),
    ('Sicoob', '756 - BANCO COOPERATIVO DO BRASIL S.A. - BANCOOB'),
    ('Inter','BANCO INTER'),
    ('Neon', 'BANCO NEON'),
    ('Nubank', 'BANCO NUBANK'),
    ('Pagseguro', 'BANCO PAGSEGURO'),
    ('Banco Original', 'BANCO ORIGINAL'),
    ('Safra', 'BANCO SAFRA'),
    ('Modal', 'BANCO MODAL'),
    ('Banestes', 'BANCO BANESTES'),
    ('Money Plus', 'MONEY PLUS'),
    ('Mercantil do Brasil', 'BANCO MERCANTIL DO BRASIL'),
    ('Gerencianet', 'GERENCIANET PAGAMENTOS DO BRASIL'),
    ('Banrisul', 'BANCO BANRISUL'),
    ('BRB', 'BRB - BANCO DE BRASÍLIA'),
    ('Via Credi', 'BANCO VIA CREDI'),
    ('Unicred', 'UNICRED'),
    ('Next', 'NEXT BANK'),
    ('Agibank', 'BANCO AGIBANK S.A.'),
    ('Banpará', 'BANCO DO ESTADO DO PARÁ S.A. - BANPARÁ'),
    ('Votorantim', 'BANCO VOTORANTIM S.A.'),
    ('JP Morgan', 'Banco J.P. Morgan S.A.'),
    ('Banco C6', 'BANCO C6 S.A. - C6 Bank'),
    ('BS2', 'BANCO BS2 S.A.'),
    ('Banco Topázio', 'BANCO TOPÁZIO S.A.'),
    ('Uniprime', 'UNIPRIME CENTRAL CCC LTDA'),
    ('Stone', 'STONE PAGAMENTOS S.A.'),
    ('Banco Daycoval', 'BANCO DAYCOVAL S.A.'),
    ('Rendimento', 'BANCO RENDIMENTO S.A.'),
    ('Banco do Nordeste', 'BANCO DO NORDESTE DO BRASIL S.A.'),
    ('Citibank', 'BANCO CITIBANK S.A.'),
    ('PJbank', 'PJBANK'),
    ('Ccc Noroeste Brasileiro', 'COOPERATIVA CENTRAL DE CREDITO NOROESTE BRASILEIRO LTDA'),
    ('Uniprime Norte do Paraná', 'UNIPRIME NORTE DO PARANÁ'),
    ('Global SCM', 'GLOBAL SCM'),
    ("Mercado Pago", "323 - MERCADO PAGO"),
    ("PicPay", "380 - PICPAY"),
]

BANCOS_NUMEROS = {
    'Banco do Brasil': '001',
    'Santander': '033',
    'Caixa Econômica': '104',
    'Bradesco': '237',
    'Itaú': '341',
    'Banrisul': '041',
    'Sicredi': '748',
    'Sicoob': '756',
    'Inter': '077',
    'BRB': '070',
    'Via Credi': '085',
    'Neon': '655',
    'Nubank': '260',
    'Pagseguro': '290',
    'Banco Original': '212',
    'Safra': '422',
    'Modal': '746',
    'Banestes': '021',
    'Unicred': '136',
    'Money Plus': '274',
    'Mercantil do Brasil': '389',
    'Gerencianet': '364',
    'Next': '237',
    'Agibank': '121',
    'Banpará': '037',
    'Votorantim': '655',
    'JP Morgan': '376',
    'Banco C6': '336',
    'BS2': '218',
    'Banco Topázio': '082',
    'Uniprime': '099',
    'Stone': '197',
    'Banco Daycoval': '707',
    'Rendimento': '633',
    'Banco do Nordeste': '004',
    'Citibank': '745',
    'PJBank': '301',
    'Ccc Noroeste Brasileiro': '097',
    'Uniprime Norte do Paraná': '084',
    'Global SCM': '384',
    'Mercado Pago': '323',
    'PicPay': '380',
}


TIPO_CONTA = [
    ('Corrente', 'CONTA CORRENTE'),
    ('Poupança', 'POUPANÇA')
]

class PaymentForm(BestPraticesModel):
    description = models.CharField(max_length=200, blank=True)

    class Meta:
        verbose_name = "Payment Form"

    def __str__(self):
        return '{}'.format(self.description)


class CreditCard(BestPraticesModel):
    """
    Model for Credit Card object
    """
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING)
    card_data = JSONField(verbose_name=_('card data'), default=dict)
    iugu_payment_token = JSONField(verbose_name=_('iugu payment token'), default=dict)

    class Meta:
        verbose_name = "Credit Card"

    def __str__(self):
        return '**** {}'.format(self.card_data['data']['number'][-4:])


class Transaction(BestPraticesModel):
    """
    Model for Transactions
    """
    types = Choices('professional', 'marketplace', 'tax', 'executive', 'discount','tax_interest')
    type = models.CharField(max_length=20,choices=types, db_index=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_recebido = models.BooleanField(default=False)
    attendance = models.ForeignKey('service_core.Attendance', null=True, blank=True, on_delete=models.DO_NOTHING)
    transfer = models.ForeignKey('Transfer', null=True, blank=True, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = "Transaction"

    def __str__(self):
        return '{}-{} R${}'.format(self.attendance_id,self.type,self.price)


class BankAccount(BestPraticesModel):
    """
    Model for Bank Accounts
    """
    bank = models.CharField(max_length=100, choices=BANCOS, verbose_name='Banco')
    agency = models.CharField(max_length=10, verbose_name='Agência com dígito')
    account_number = models.CharField(max_length=10, verbose_name='Número da Conta com dígito')
    operation_code = models.CharField(max_length=10, null=True, blank=True, verbose_name='Código de operação')
    account_type = models.CharField(max_length=10, choices=TIPO_CONTA, verbose_name='Tipo da conta')

    def __str__(self):
        return self.account_number

    @property
    def get_formated_account_number(self):
        bank = self.bank
        account_number = self.account_number
        string_size = 8
        if bank in ['Banco do Brasil', 'Santander', 'Pagseguro', 'Banestes', 'Money Plus', 'Mercantil do Brasil', 'Gerencianet']:
            account_number = '{}-{}'.format(account_number[:-1].rjust(string_size, '0'),account_number[-1])
        elif bank == 'Caixa Econômica':
            account_number = '{}{}-{}'.format(self.operation_code,account_number[:-1].rjust(string_size, '0'), account_number[-1])
        elif bank in ['Bradesco','Neon', 'Next', 'Banco C6', 'Stone', 'Ccc Noroeste Brasileiro']:
            string_size = 7
            account_number = '{}-{}'.format(account_number[:-1].rjust(string_size, '0'), account_number[-1])
        elif bank in ['Itaú', 'Banco Original', 'Banco Topázio', 'Uniprime']:
            string_size = 5
            account_number = '{}-{}'.format(account_number[:-1].rjust(string_size, '0'), account_number[-1])
        elif bank in ['Banrisul', 'Sicoob', 'Inter', 'BRB', 'Modal', 'Banpará', 'Votorantim']:
            string_size = 9
            account_number = '{}-{}'.format(account_number[:-1].rjust(string_size, '0'), account_number[-1])
        elif bank in ['Nubank', 'PJBank']:
            string_size = 10
            account_number = '{}-{}'.format(account_number[:-1].rjust(string_size, '0'), account_number[-1])
        elif bank in ['Via Credi', 'JP Morgan']:
            string_size = 11
            account_number = '{}-{}'.format(account_number[:-1].rjust(string_size, '0'), account_number[-1])
        elif bank in ['BS2', 'Banco Daycoval', 'Banco do Nordeste', 'Uniprime Norte do Paraná']:
            string_size = 6
            account_number = '{}-{}'.format(account_number[:-1].rjust(string_size, '0'), account_number[-1])
        elif bank == 'Sicredi':
            account_number = account_number.rjust(6, '0')
        elif bank == 'Citibank':
            account_number = account_number.rjust(8, '0')
        elif bank in ['Agibank', 'Rendimento']:
            account_number = account_number.rjust(10, '0')
        elif bank in ['Global SCM']:
            account_number = account_number.rjust(11, '0')
        return account_number

    @property
    def get_formated_agency(self):
        bank = self.bank
        agency = self.agency
        string_size = 4
        if bank in ['Banco do Brasil', 'Bradesco', 'Rendimento', 'Next']:
            agency = '{}-{}'.format(agency[:-1].rjust(string_size, '0'), agency[-1])
        else:
            if bank == 'Money Plus':
                string_size = 1
            if bank == 'Banco do Nordeste':
                string_size = 3
            agency = agency.rjust(string_size, '0')
        return agency

    @property
    def get_formated_account_type(self):
        accout_type = self.account_type
        if accout_type == 'Corrente':
            return 'cc'
        return 'cp'

    @property
    def get_bank_number(self):
        return BANCOS_NUMEROS[self.bank]


class Campaign(BestPraticesModel):
    """
    Model for Campaigns
    """
    name = models.CharField(max_length=200)
    executive = models.ForeignKey(Executive, null=True, blank=True, verbose_name='Executivo')
    slug = models.SlugField(max_length=250, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.slug == "":
            self.slug = slug_generator(slug_generator("{}{}".format(self.name, datetime.now())))
        return super(Campaign, self).save(*args, **kwargs)


class VoucherCustomer(BestPraticesModel):
    """
    Stores Vouchers(:model:`payment.voucher`) for a Customer(:model:`customer.customer`)
    """
    voucher = models.ForeignKey('Voucher')
    customer = models.ForeignKey(Customer)

    def __str__(self):
        return '{}'.format(self.id)


class Voucher(BestPraticesModel):
    """
    Model for Vouchers
    """
    types = Choices('total', 'marketplace')
    discount_types = Choices(('percent', 'Percentual'), ('value', 'Valor Exato'))
    validation_types = Choices(('one_use', 'Uso Único'), ('multiple_use', 'Usos Múltiplos'))
    initial_date = models.DateTimeField(verbose_name='Data Inicial')
    final_date = models.DateTimeField(verbose_name='Data Final')
    service = models.ForeignKey('service_core.Service', null=True, blank=True)
    type = models.CharField(default='total', max_length=20, choices=types, db_index=True)
    validation_type = models.CharField(default='one_use', max_length=20, choices=validation_types, db_index=True, verbose_name='Tipo de Validação')
    discount_type = models.CharField(default='percent', max_length=20, choices=discount_types, db_index=True, verbose_name='Tipo de Desconto')
    code = models.SlugField(max_length=20, unique=True, blank=True, auto_created=True, verbose_name='Código Promocional')
    campaign = models.ForeignKey(Campaign, null=True, blank=True)
    discount = models.IntegerField(default=0, verbose_name='Desconto')
    discount_value = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    has_used = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=0, verbose_name='Quantidade')
    quantity_used = models.PositiveIntegerField(default=0)
    observation = models.TextField(max_length=500, null=True, blank=True, verbose_name='Observações')
    executive = models.ForeignKey('professional.Executive', null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name="Ativo")

    def __str__(self):
        return self.code

    def validate_voucher(self, customer_id, service_id, attendance_value, attendance_scheduling_date):
        response = dict()
        response['discount_value'] = 0
        response['is_valid'] = False
        response['error_message'] = ''
        if (datetime.now() >= self.initial_date) and (datetime.now() <= self.final_date):
            if self.service is None or (self.service_id == service_id):
                if self.validation_type == 'one_use':
                    if not self.has_used:
                        response['is_valid'] = True
                    else:
                        response['error_message'] = 'Voucher já utilizado'
                elif self.validation_type == 'multiple_use':
                    if self.quantity_used < self.quantity:
                        response['is_valid'] = True
                    else:
                        response['error_message'] = 'Voucher já excedeu o limite de utilizações'
            else:
                response['error_message'] = 'Voucher não válido para esse tipo de serviço'
        else:
            response['error_message'] = 'Voucher não válido para a data do atendimento ele é válido de ' \
                                        '{} à {}'.format(self.initial_date.date(), self.final_date.date(),)
        if response['is_valid']:
            if self.discount_type == 'percent':
                response['discount_value'] = float(attendance_value * self.discount / 100)
            else:
                response['discount_value'] = float(self.discount_value)
        return response

    def use_voucher(self, customer_id):
        if self.validation_type == 'one_use':
            self.has_used = True
        elif self.validation_type == 'multiple_use':
            if self.quantity_used < self.quantity:
                self.quantity_used += 1
        self.save()
        if customer_id:
            VoucherCustomer.objects.get_or_create(voucher=self,customer_id=customer_id)
        return False


class Transfer(BestPraticesModel):
    """
    Model for Transfers
    """
    professional = models.ForeignKey('professional.Professional')
    transfer_iugu_id = models.CharField(max_length=40, null=True, blank=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, default='pending', choices=(('pending', 'Pendente'), ('processing', 'Processando'), ('accepted', 'Concluída'), ('rejected', 'Rejeitada')))
    observation = models.CharField(max_length=300, blank=True)
    bank_account = models.ForeignKey('BankAccount', null=True, blank=True, on_delete=models.DO_NOTHING)
    information_data = JSONField(verbose_name=_('information_data'), default=dict)

    def __str__(self):
        return '{}'.format(self.id)


class Payment(BestPraticesModel):
    """
    Model for Payments
    """
    attendance = models.ForeignKey('service_core.Attendance', null=True, blank=True, on_delete=models.DO_NOTHING, related_name='payments')
    invoice_id = models.CharField(max_length=40, unique=True)
    amount = models.DecimalField(decimal_places=2, max_digits=12, default=0)
    status = models.CharField(max_length=10, default='pending', choices=(('pending', 'Pendente'), ('processing', 'Processando'), ('accepted', 'Concluída'), ('rejected', 'Rejeitada'), ('refunded', 'Reembolsado')))
    information_data = JSONField(verbose_name=_('information_data'), default=dict)

    def __str__(self):
        return '{}'.format(self.id)


class PaymentInstallment(BestPraticesModel):
    """
    Stores Installments of a Payment(:model:`payment.payment`)
    """
    payment = models.ForeignKey(Payment, null=True, blank=True, on_delete=models.DO_NOTHING)
    installment_id = models.PositiveIntegerField(unique=True)
    installment_data = JSONField(verbose_name=_('information_data'), default=dict)
    is_received = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.id)
