from django import forms
from django.utils.translation import ugettext_lazy as _

from apps.common.models import Address

from .models import ExecutiveLead, ProfissionalLead


class SimpleExecutiveLeadForm(forms.ModelForm):

    class Meta:
        model = ExecutiveLead
        fields = ('name', 'cpf', 'email', 'telephone',)

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Nome'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control cpf', 'placeholder':'CPF'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'E-mail'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control celphones', 'placeholder': 'Telefone', 'required': True}),
        }


class ExecutiveLeadForm(forms.ModelForm):
    
    class Meta:
        model = ExecutiveLead
        fields = ('name', 'cpf', 'rg', 'gender', 'civil_status', 'birthdate', 'telephone', 'celphone', )

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Nome', 'required':True}),
            'cpf': forms.TextInput(attrs={'class': 'form-control cpf', 'placeholder':'CPF', 'required':True}),
            'rg': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'RG', 'required':True}),
            'gender': forms.Select(attrs={'class': 'form-control', 'required':True}),
            'civil_status': forms.Select(attrs={'class': 'form-control', 'required':True}),
            'birthdate': forms.TextInput(attrs={'class': 'form-control date', 'placeholder':'Data de nascimento','required':True}),
            'telephone': forms.TextInput(attrs={'class': 'form-control celphones', 'placeholder':'Telefone', 'required':True}),
            'celphone': forms.TextInput(attrs={'class': 'form-control celphones', 'placeholder':'Celular', 'required':True}),
        }
       

class AddressLeadForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ('postal_code', 'address', 'number','complemento', )

        widgets = {
            'postal_code': forms.TextInput(attrs={'class': 'form-control cep', 'placeholder':'CEP', 'required':True}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Logradouro', 'required':True}),
            'number': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Número', 'required':True}),
            'complemento': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Complemento', 'required': False}),
        }


class SimpleProfissionalLeadForm(forms.ModelForm):

    class Meta:
        model = ProfissionalLead
        fields = ('name', 'email', 'category', 'telephone',)

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder':'Nome'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder':'Email'}),
            'category': forms.SelectMultiple(attrs={'class': 'categoria select2'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control celphones', 'placeholder': 'Telefone', 'required': True}),
        }


class ProfissionalLeadForm(forms.ModelForm):
    
    class Meta:
        model = ProfissionalLead
        fields = ('name', 'cpf', 'rg', 'gender', 'civil_status', 'birthdate', 'telephone', 'celphone', 'executive',
                  'category', 'status', 'obs', 'email')

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required':True}),
            'cpf': forms.TextInput(attrs={'class': 'form-control cpf'}),
            'rg': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'civil_status': forms.Select(attrs={'class': 'form-control'}),
            'birthdate': forms.TextInput(attrs={'class': 'form-control date'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control celphones', 'required':True}),
            'celphone': forms.TextInput(attrs={'class': 'form-control celphones'}),
            'categorias': forms.Select(attrs={'class': 'form-control show-tick', 'required':True}),
            'obs': forms.Textarea(attrs={'class': 'form-control  no-resize'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),

        }
