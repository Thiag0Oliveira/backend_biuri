from apps.common.models import Address
from .marketplace import MarketPlace
from apps.common.fields import JSONField
from django.db import models
from .transfer import Transfer as IuguTransfer
from .customer import Customer as IuguCustomer
from django.utils.translation import ugettext_lazy as _



class IuguMarketplaceAccount(models.Model):
    """
    Model for Iugu Accounts
    """
    address = models.ForeignKey(Address, null=True, blank=True)
    bank_account = models.ForeignKey('payment.BankAccount', null=True, blank=True)
    cellphone = models.CharField(max_length=11, null=True, blank=True, verbose_name='Telefone')
    iugu_account_id = models.CharField(max_length=40, null=True, blank=True)
    iugu_account_data = JSONField(verbose_name=_('iugu account data'), default=dict)
    iugu_account_verification = JSONField(verbose_name=_('iugu verification data'), default=dict)

    class Meta:
        abstract = True

    def transfer_iugu(self, amount_cents):
        data = {'receiver_id': self.iugu_account_data['account_id'], 'amount_cents': amount_cents}
        transfer = IuguTransfer()
        transfer = transfer.create(data=data)
        return transfer

    def create_account_iugu(self):
        account = MarketPlace()
        if not self.iugu_account_id:
            print('entrei aqui')
            sub_account_iugu = {}
            sub_account_iugu['commissions'] = {'percent': 30, 'credit_card_percent': 30}
            account_data = account.create(data=sub_account_iugu)
            self.iugu_account_data = account_data
            self.iugu_account_id = account_data['account_id']
            self.save()
        else:
            account_data = self.iugu_account_data
            verification_data = self.iugu_account_verification
            # if (verification_data == {"errors": {"account": ["conta já verificada"]}}):
            #     self.professional_verified = True
            #     self.save()
            if (verification_data == {} or (verification_data != {"errors": {"account": ["conta já verificada"]}} and "errors" in verification_data)):
                account_verification_data = {'price_range': 'Mais que R$ 500,00',
                                             'physical_products': False,
                                             'business_type': 'Serviços de Beleza',
                                             'automatic_transfer': True,
                                             'address': self.address.address,
                                             'cep': self.address.postal_code,
                                             'city': self.address.city,
                                             'state': self.address.state,
                                             'telephone': self.cellphone,
                                             'bank': self.bank_account.bank,
                                             'bank_ag': self.bank_account.get_formated_agency,
                                             'account_type': self.bank_account.account_type,
                                             'bank_cc': self.bank_account.get_formated_account_number}
                if len(self.user.username) == 11:
                    person_type_data = {
                        'cpf': self.user.username,
                        'resp_cpf': self.user.username,
                        'person_type': 'Pessoa Física',
                        'name': self.user.get_full_name(),
                        'resp_name': self.user.get_full_name(),
                    }
                else:
                    person_type_data = {
                        'cnpj': self.user.username,
                        'person_type': 'Pessoa Jurídica',
                        'company_name': self.user.get_full_name(),
                    }
                account_verification_data.update(person_type_data)
                account_verification = account.request_verification(id=account_data['account_id'],
                                                                    data={'data': account_verification_data},
                                                                    api_token=account_data['live_api_token'])
                self.iugu_account_verification = account_verification
                self.save()
            else:
                account_verification_data = {'bank': self.bank_account.get_bank_number,
                                             'agency': self.bank_account.get_formated_agency,
                                             'account_type': self.bank_account.get_formated_account_type,
                                             'account': self.bank_account.get_formated_account_number}
                account_verification = account.update_bank_data(id=account_data['account_id'],
                                                                data=account_verification_data,
                                                                api_token=account_data['live_api_token'])
                self.iugu_account_verification = account_verification
                self.save()
        return 'success'


class IuguCustomerCompanyAccount(models.Model):
    """
    Model for Companies' Iugu Account
    """
    address = models.ForeignKey(Address, null=True, blank=True)
    iugu_client_id = models.CharField(max_length=40, null=True, blank=True)
    iugu_client_data = JSONField(verbose_name=_('iugu account data'), default=dict)

    class Meta:
        abstract = True

    def create_account_iugu(self):
        data = {
            'cpf_cnpj': self.cnpj,
            'email': self.email,
            'name': self.company_name,
            'zip_code': self.address.postal_code,
            'number': self.address.number,
            'street': self.address.address,
            'city': self.address.city,
            'state': self.address.state,
            'district': self.address.neighborhood,
            'complement': self.address.complemento
        }
        iugu = IuguCustomer().create(data)
        self.iugu_client_id = iugu['id']
        self.iugu_client_data = iugu
        self.save()
        return 'success'


class IuguInvoice(models.Model):
    """
    Model for Iugu Invoices
    """
    invoice_id = models.CharField(max_length=40, unique=True, null=True, blank=True)
    information_data = JSONField(verbose_name=_('information_data'), default=dict, blank=True)

    class Meta:
        abstract = True

    def update_data_iugu(self, data):
        self.invoice_id = data['invoice_id']
        self.information_data = data
        self.save()
