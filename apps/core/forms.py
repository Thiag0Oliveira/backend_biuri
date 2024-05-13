from django import forms
from django.contrib.auth.models import User

from pycpfcnpj import cpfcnpj

from apps.common.models import Address, UserAddress


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['number'].widget.attrs['class'] = 'form-control'
        self.fields['complemento'].widget.attrs['class'] = 'form-control'
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['postal_code'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['class'] = 'form-control'
        self.fields['neighborhood'].widget.attrs['class'] = 'form-control'


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = UserAddress
        exclude = ['user',]

    def __init__(self, *args, **kwargs):
        super(UserAddressForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['number'].widget.attrs['class'] = 'form-control'
        self.fields['complemento'].widget.attrs['class'] = 'form-control'
        self.fields['address'].widget.attrs['class'] = 'form-control'
        self.fields['postal_code'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['class'] = 'form-control'
        self.fields['neighborhood'].widget.attrs['class'] = 'form-control'


class CustomUserForm(forms.ModelForm):
    username = forms.CharField(max_length=14)

    def __init__(self, *args, **kwargs):
        super(CustomUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].label = 'Nome'
        self.fields['last_name'].label = 'Sobrenome'
        self.fields['username'].label = 'CPF/CNPJ'
        self.fields['email'].label = 'E-mail'

    class Meta:
        model = User
        fields = ('first_name','last_name','username','email')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        if not cpfcnpj.validate(username):
            if len(username) == 11:
                self.add_error('username', 'CPF inválido')
            elif len(username) == 14:
                self.add_error('username', 'CNPJ inválido')
            else:
                self.add_error('username', 'Número inválido')


class CustomCustomerUserForm(forms.ModelForm):
    username = forms.CharField(max_length=11)

    def __init__(self, *args, **kwargs):
        super(CustomCustomerUserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].label = 'Nome'
        self.fields['last_name'].label = 'Sobrenome'
        self.fields['username'].label = 'CPF ou Telefone'
        self.fields['email'].label = 'E-mail'


    class Meta:
        model = User
        fields = ('first_name','last_name','username','email')

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')


class CustomCustomerUserFormWhitoutUsername(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(CustomCustomerUserFormWhitoutUsername, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['class'] = 'form-control'
        self.fields['last_name'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['first_name'].label = 'Nome'
        self.fields['last_name'].label = 'Sobrenome'
        self.fields['email'].label = 'E-mail'


    class Meta:
        model = User
        fields = ('first_name','last_name','email')

    def clean(self):
        cleaned_data = super().clean()