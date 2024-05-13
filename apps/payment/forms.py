from django import forms

from .models import BankAccount, CreditCard, Voucher


class BankAccountForm(forms.ModelForm):

    class Meta:
        model = BankAccount
        exclude = ['is_removed',]

    def __init__(self,*args, **kwargs):
        super(BankAccountForm, self).__init__(*args, **kwargs)
        self.fields['bank'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['agency'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['account_number'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['account_type'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['operation_code'].widget.attrs['class'] = 'form-control  no-resize'


class CreditCardForm(forms.ModelForm):

    class Meta:
        model = CreditCard
        fields = ['card_data', 'iugu_payment_token']


class VoucherForm(forms.ModelForm):

    class Meta:
        model = Voucher
        fields = ['code', 'initial_date', 'final_date', 'validation_type', 'discount_type', 'discount', 'discount_value', 'quantity', 'observation']

    def __init__(self, *args, **kwargs):
        super(VoucherForm, self).__init__(*args, **kwargs)
        self.fields['initial_date'].widget.attrs['class'] = 'datetimepicker form-control'
        self.fields['final_date'].widget.attrs['class'] = 'datetimepicker form-control'
        self.fields['initial_date'].widget.attrs['data-dtp'] = 'dtp_6VyeJ'
        self.fields['final_date'].widget.attrs['data-dtp'] = 'dtp_6VyeJ'
        self.fields['validation_type'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['discount_type'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['code'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['discount'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['discount_value'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['quantity'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['observation'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['discount_value'].required = False
        self.fields['discount'].required = False

    def clean(self):
        cleaned_data = super().clean()
        discount_type = cleaned_data.get('discount_type')
        discount = cleaned_data.get('discount')
        discount_value = cleaned_data.get('discount_value')
        if discount_type == 'percent' and discount_value is not None:
            if discount_value % 1 != 0:
                self.add_error('discount_value', 'Informe um valor inteiro')
        if discount_type == 'value':
            self.instance.discount_value = discount
            self.instance.discount = 0