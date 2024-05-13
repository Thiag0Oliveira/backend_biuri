from celery import shared_task
from django.db.models import Sum
from django.db.models.functions import Coalesce
from datetime import datetime, timedelta

from apps.iugu.transfer import Transfer as IuguTransfer
from apps.iugu.transaction import Transaction as IuguTransaction
from apps.payment.models import Transaction, Transfer, PaymentInstallment
from .models import Professional, Executive
from apps.iugu.marketplace import MarketPlace
from oauth2_provider.models import AccessToken

@shared_task
def enabled_accounts():
    professionals = Professional.objects.filter(professional_verified=False, professional_enabled=True)
    for professional in professionals:
        create_account_iugu(professional.pk)
    return 'success'

@shared_task
def create_account_iugu(professional_id):
    professional = Professional.objects.get(pk=professional_id)
    professional.create_account_iugu()
    return 'success'

def get_professionals(type):
    return

def transactions_advanced(professional_id):
    installments = PaymentInstallment.objects.filter(is_received=False,
                                                     payment__attendance__professional_id=professional_id)
    installments = list(installments.values_list('installment_id', flat=True))
    if len(installments) > 0:
        installment_iugu = IuguTransaction()
        installment_iugu.advance(data={'transactions': installments})
    return 'success'

@shared_task
def transfers():
    professionals = Professional.objects.all()
    for professional in professionals:
        create_transfer.delay(professional.pk)
    return 'success'


@shared_task
def transfers_executive():
    executives = Executive.objects.all()
    for executive in executives:
        create_transfer_executive.delay(executive.pk)
    return 'success'

@shared_task
def create_transfer(professional_id):
    professional = Professional.objects.get(pk=professional_id)
    transactions = Transaction.objects.filter(attendance__professional=professional, type='professional', is_recebido=False)
    transactions_total = transactions.aggregate(y=Coalesce(Sum('price'),0))
    transfer = {}
    if transactions.exists():
        amount = int(float(transactions_total['y']) * 100)
        transactions_advanced(professional_id)
        transfer = professional.transfer_iugu(amount_cents=amount)
        transfer_model = Transfer(professional=professional,
                                  total=transactions_total['y'],
                                  transfer_iugu_id= transfer['id'] if 'id' in transfer else '',
                                  bank_account=professional.bank_account,
                                  information_data=transfer)
        transfer_model.save()
        if 'id' in transfer:
            transactions.update(is_recebido=True, transfer=transfer_model)
            transaction_executivo = Transaction(price=-2,type='executive', transfer=transfer_model)
            transaction_executivo.save()
    return transfer


@shared_task
def create_account_iugu_executive(executive_id):
    executive = Executive.objects.get(pk=executive_id)
    executive.create_account_iugu()
    return 'success'


@shared_task
def create_transfer_executive(executive_id):
    executive = Executive.objects.get(pk=executive_id)
    transactions = Transaction.objects.filter(attendance__professional__executive=executive,
                                              type='executive', is_recebido=False)
    transactions_total = transactions.aggregate(y=Coalesce(Sum('price'),0))
    transfer = {}
    if transactions.exists():
        amount = int(float(transactions_total['y']) * 100)
        transfer = executive.transfer_iugu(amount_cents=amount)
        if 'id' in transfer:
            transfer_model = Transfer(total=transactions_total['y'],
                                      transfer_iugu_id=transfer['id'],
                                      bank_account=executive.bank_account)
            transfer_model.save()
            transactions.update(is_recebido=True, transfer=transfer_model)
    return transfer


@shared_task
def update_access_token():
    expires = datetime.now() + timedelta(days=180)
    access_token = AccessToken.objects.all().update(expires=expires)