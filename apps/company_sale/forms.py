from django import forms
from . import models


class CompanyForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.fields['cnpj'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['state_registration'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['company_name'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['trading_name'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['phone'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['email'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['contact_name'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['contact_cellphone'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['contact_email'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['observation'].widget.attrs['class'] = 'form-control no-resize'

    class Meta:
        model = models.Company
        fields = ['cnpj', 'state_registration', 'company_name', 'trading_name', 'phone', 'email', 'address',
                  'contact_name', 'contact_cellphone', 'contact_email', 'observation']

    def _save_m2m(self):
        return 'success'


class SaleForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SaleForm, self).__init__(*args, **kwargs)
        self.fields['commission'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['status'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['observation'].widget.attrs['class'] = 'form-control  no-resize'

    class Meta:
        model = models.Sale
        fields = ['company', 'seller', 'executive', 'commission', 'observation', 'status']


class SaleVoucherGeneratorForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SaleVoucherGeneratorForm, self).__init__(*args, **kwargs)
        self.fields['quantity'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['value'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['observation'].widget.attrs['class'] = 'form-control no-resize'
        self.fields['initial_date'].widget.attrs['class'] = 'datetimepicker form-control'
        self.fields['final_date'].widget.attrs['class'] = 'datetimepicker form-control'
        self.fields['initial_date'].widget.attrs['data-dtp'] = 'dtp_6VyeJ'
        self.fields['final_date'].widget.attrs['data-dtp'] = 'dtp_6VyeJ'
        self.fields['service'].empty_label = 'Qualquer serviço'

    class Meta:
        model = models.SaleVoucherGenerator
        fields = ['service', 'quantity', 'value', 'observation', 'initial_date', 'final_date']
