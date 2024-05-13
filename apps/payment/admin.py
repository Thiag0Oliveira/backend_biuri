from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from .models import CreditCard, PaymentForm, Transaction, Voucher, Campaign, BankAccount, Transfer, Payment, \
    PaymentInstallment

class PaymentAdmin(admin.ModelAdmin):
	raw_id_fields = ['attendance',]

class TransactionAdmin(admin.ModelAdmin):
	raw_id_fields = ['attendance', 'transfer']

admin.site.register(PaymentForm,SimpleHistoryAdmin)
admin.site.register(CreditCard,SimpleHistoryAdmin)
admin.site.register(BankAccount)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Voucher)
admin.site.register(Campaign)
admin.site.register(Transfer)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(PaymentInstallment)