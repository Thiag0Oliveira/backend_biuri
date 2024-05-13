from itertools import chain

from django import forms
from datetime import datetime
from django.core.cache import cache
from django.forms.models import inlineformset_factory
from django.forms.widgets import CheckboxInput, SelectMultiple
from django.utils.encoding import force_str
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from apps.common.models import UserAddress
from apps.core.models import City, Neighborhood
from apps.customer.models import Customer
from apps.payment.models import BankAccount
from apps.professional.models import Professional
from apps.service_core.models import Category, Service, PricingCriterion, PricingCriterionOptions, Attendance

from . import models
from ..message_core.models import PushSchedule


class CheckboxSelectMultiple(SelectMultiple):
    def render(self, name, value, attrs=None, choices=()):
        if value is None: value = []
        has_id = attrs and 'id' in attrs
        final_attrs = self.build_attrs(attrs)
        output = [u'<ul style="list-style-type:none">']
        # Normalize to strings
        str_values = set([force_str(v) for v in value])
        for i, (option_value, option_label) in enumerate(chain(self.choices, choices)):
            # If an ID attribute was given, add a numeric index as a suffix,
            # so that the checkboxes don't all have the same ID attribute.
            if has_id:
                final_attrs = dict(final_attrs, id='%s_%s' % (attrs['id'], i))
                label_for = u' for="%s"' % final_attrs['id']
            else:
                label_for = ''

            cb = CheckboxInput(final_attrs, check_test=lambda value: value in str_values)
            option_value = force_str(option_value)
            rendered_cb = cb.render(name, option_value)
            option_label = conditional_escape(force_str(option_label))
            output.append(u'<li>%s<label %s>%s </label></li>' % (rendered_cb,label_for, option_label))
        output.append(u'</ul>')
        return mark_safe(u'\n'.join(output))

    def id_for_label(self, id_):
        # See the comment for RadioSelect.id_for_label()
        if id_:
            id_ += '_0'
        return id_


class ProfessionalForm(forms.ModelForm):
    badges = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple(),queryset=models.Badge.objects.all(), required=False)
    categorias = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple(), queryset=Category.objects.all(), required=False)
    cidades = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple(), queryset=City.objects.filter(is_covered=True), required=False)
    days_of_week = forms.MultipleChoiceField(widget=CheckboxSelectMultiple(), choices=models.DAYS_OF_WEEK, label='Disponibilidade na semana', required=False)
    documents = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}), required=False)

    def __init__(self, *args, **kwargs):
        super(ProfessionalForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['instagram_username'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['observation'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['celphone'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['categorias'].widget.attrs['class'] = 'form-control show-tick'
        self.fields['badges'].widget.attrs['class'] = 'form-control show-tick'
        self.fields['cidades'].widget.attrs['class'] = 'form-control'
        self.fields['attendance_percent'].widget.attrs['class'] = 'form-control'
        self.fields['full_name'].widget.attrs['class'] = 'form-control'
        self.fields['attendance_window'].widget.attrs['class'] = 'form-control'

        self.fields['cidades'].queryset = City.objects.filter(is_covered=True)
        instance = getattr(self, 'instance', None)
        if instance.pk is not None:
            days_of_week = models.ProfessionalScheduleDefault.objects.filter(professional=instance).values_list('day_of_week')
            days_of_week_list = []
            for day in days_of_week:
                days_of_week_list.append(day[0])
            self.fields['days_of_week'].initial = days_of_week_list

    def _save_m2m(self):
        return 'success'

    def clean(self):
        super(ProfessionalForm, self).clean()  # if necessary
        if 'cidades' in self._errors:
            del self._errors['cidades']
        return self.cleaned_data

    class Meta:
        model = models.Professional
        # exclude = ('is_removed','iugu_account_data','evaluations','attendance_completed_count',
        #            'attendance_cancelation_count', 'rating', 'address','neighborhoods', 'user','send_sms',
        #            'iugu_account_id','iugu_account_verification','professional_verified','search_text')
        fields = ('description','observation','avatar','badges','category','is_saloon', 'professional_enabled',
                  'professional_enabled_executive','bank_account','executive','celphone','birthday',
                  'gender','gender_attendance','categorias','cidades','instagram_username','attendance_percent',
                  'status','payment_frequency','documents', 'full_name', 'attendance_window', )


class ServiceProfessionalForm(forms.ModelForm):

    class Meta:
        model = models.ServiceProfessional
        fields = '__all__'
        exclude = ('is_removed',)


class ProfessionalCityForm(forms.ModelForm):
    neighborhoods = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple(),queryset=models.Neighborhood.objects.all())

    class Meta:
        model = models.ProfessionalCity
        exclude = ['professional','is_removed']

    def __init__(self, *args, **kwargs):
        super(ProfessionalCityForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        city = instance.city
        self.fields['neighborhoods'].queryset = Neighborhood.objects.filter(city=city, father__isnull=True).order_by('zone', 'description')
        if instance:
            self.fields['city'].queryset = City.objects.filter(pk=city.pk)


class ProfessionalCategoryForm(forms.ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), label='Categoria')
    services = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple(), queryset=Service.objects.all().order_by('name'))

    class Meta:
        model = models.ProfessionalCategory
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(ProfessionalCategoryForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['services'].queryset = Service.objects.filter(category=instance.category, can_set_price=True).order_by('name')


class ProfessionalCriterionForm(forms.ModelForm):
    pricing_criterion = forms.ModelChoiceField(queryset=PricingCriterion.objects.all(), label='Categoria')
    pricing_criterion_option = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple(),
                                                               queryset=PricingCriterionOptions.objects.all()
                                                               .order_by('name'), required=False)

    class Meta:
        model = models.ProfessionalCriterion
        exclude = ['professional',]

    def __init__(self, *args, **kwargs):
        super(ProfessionalCriterionForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['pricing_criterion_option'].queryset = PricingCriterionOptions.objects.filter(pricing_criterion=instance.pricing_criterion)


class ProfessionalDocumentForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ProfessionalDocumentForm, self).__init__(*args, **kwargs)
        self.fields['document_type'].widget.attrs['class'] = 'form-control  no-resize'

    class Meta:
        model = models.ProfessionalDocument
        fields = ['document', 'document_type']


class ProfessionalServiceForm(forms.ModelForm):

    class Meta:
        model = models.ServiceProfessional
        fields = ['minimum_price','maximum_price','average_time']


class ProfessionalPricingCriterionServiceForm(forms.ModelForm):

    class Meta:
        model = models.ServiceProfessionalPricingCriterion
        fields = ['price','average_time']


class ProfessionalScheduleDefaultForm(forms.ModelForm):
    provide_all_day = forms.BooleanField(widget=CheckboxInput(attrs={'onclick': "ClickCheckbox(this)"}), label="Todo o dia", required=False)
    dawn_morning = forms.BooleanField(widget=CheckboxInput(attrs={'onclick': "ClickCheckbox(this)", 'onchange': "ChangeCheckboxElements(this)"}), label="Madrugada/Manhã", required=False)
    afternoon_night = forms.BooleanField(widget=CheckboxInput(attrs={'onclick': "ClickCheckbox(this)", 'onchange': "ChangeCheckboxElements(this)"}), label="Tarde/Noite", required=False)
    dawn_morning_range_begin = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'class': "form-control time24"}))
    dawn_morning_range_end = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'class': "form-control time24"}))
    afternoon_night_range_begin = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'class': "form-control time24"}))
    afternoon_night_range_end = forms.TimeField(widget=forms.widgets.TimeInput(attrs={'class': "form-control time24"}))

    class Meta:
        model = models.ProfessionalScheduleDefault
        exclude = ['is_removed']


class ExecutiveForm(forms.ModelForm):
    cidades = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple(),
                                             queryset=City.objects.filter(is_covered=True), required=False)

    def __init__(self, *args, **kwargs):
        super(ExecutiveForm, self).__init__(*args, **kwargs)
        self.fields['cellphone'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['cidades'].widget.attrs['class'] = 'form-control'
        self.fields['cidades'].queryset = City.objects.filter(is_covered=True)

    class Meta:
        model = models.Executive
        fields = ['address', 'bank_account', 'cellphone', 'cidades', 'avatar']

    def _save_m2m(self):
        return 'success'


class SellerForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(SellerForm, self).__init__(*args, **kwargs)
        self.fields['cellphone'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['commission_percent'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['observation'].widget.attrs['class'] = 'form-control  no-resize'

    class Meta:
        model = models.Seller
        fields = ['address', 'bank_account', 'cellphone', 'commission_percent', 'observation', 'executive']

    def _save_m2m(self):
        return 'success'


class ProfessionalConciergeForm(forms.Form):
    service = forms.ModelChoiceField(queryset=Service.objects.select_related('category').filter(is_app_enabled=True)
                                     .order_by('category__name','name'), label='Serviço')
    pricing_criterion = forms.ModelChoiceField(queryset=PricingCriterionOptions.objects.none(),
                                          label='Critério de Preço', required=False)
    city = forms.ModelChoiceField(queryset=City.objects.filter(is_covered=True).order_by('name'),
                                  label='Cidade')
    neighborhood = forms.ModelChoiceField(queryset=Neighborhood.objects.none(),
                                  label='Bairro', required=False)
    date = forms.DateField(label='Data', required=False)
    time = forms.TimeField(label='Hora', required=False)
    price_min = forms.DecimalField(label='Preço Menor', required=False)
    price_max = forms.DecimalField(label='Preço Maior', required=False)

    def __init__(self, *args, **kwargs):
        super(ProfessionalConciergeForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datepicker'
        # self.fields['date'].widget.attrs['data-dtp'] = 'dtp_6VyeJ'
        self.fields['time'].widget.attrs['class'] = 'timepicker'
        # self.fields['time'].widget.attrs['data-dtp'] = 'dtp_6VyeJ'
        if 'city' in self.data:
            self.fields['neighborhood'].queryset = Neighborhood.objects.filter(city_id=self.data['city'], father__isnull=True).order_by('description')
            self.fields['neighborhood'].label_from_instance = self.label_from_instance
        # self.fields['cellphone'].widget.attrs['class'] = 'form-control  no-resize'
        # self.fields['commission_percent'].widget.attrs['class'] = 'form-control  no-resize'
        # self.fields['observation'].widget.attrs['class'] = 'form-control  no-resize'

    @staticmethod
    def label_from_instance(self):
        return str(self.description)


class ProfessionalConciergeFormPost(forms.Form):
    scheduling_date = forms.DateTimeField(label='Data Agendamento', required=False)
    celphone = forms.CharField(max_length=11, label='Telefone', required=False)
    name = forms.CharField(max_length=40, label='Nome', required=False)
    professional = forms.IntegerField(label='Profissional', required=False)
    price = forms.DecimalField(label='Preço', required=False)

    def __init__(self, *args, **kwargs):
        super(ProfessionalConciergeFormPost, self).__init__(*args, **kwargs)
        self.fields['scheduling_date'].widget.attrs['class'] = 'datetimepicker'

class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ['observation', 'observation_internal']

class CustomerForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = ['celphone', 'gender']


class PushScheduleForm(forms.ModelForm):
    cidades = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple(), queryset=City.objects.filter(is_covered=True), required=False)
    professional_categories = forms.ModelMultipleChoiceField(widget=CheckboxSelectMultiple(), queryset=Category.objects.all(), initial=Category.objects.all(), required=False)

    class Meta:
        model = PushSchedule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(PushScheduleForm, self).__init__(*args, **kwargs)
        self.fields['date_schedule'].initial = datetime.now()
        self.fields['title'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['text'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['date_schedule'].widget.attrs['class'] = 'form-control  no-resize'
        self.fields['send_customer'].widget.attrs['onclick'] = 'hideElement("id_send_customer","customer_segment")'
        self.fields['send_professional'].widget.attrs['onclick'] = 'hideElement("id_send_professional","professional_segment")'
        self.fields['send_region'].widget.attrs['onclick'] = 'hideElement("id_send_region","region_segment")'


class AttendanceConciergeForm(forms.Form):
    address = forms.ModelChoiceField(queryset=UserAddress.objects.all(),
                                    widget=forms.RadioSelect, empty_label='Adicionar Novo', required=False)

    # def __init__(self, favorite_book=None, *args, **kwargs):
    #     super(AttendanceConciergeForm, self).__init__(*args, **kwargs)

ServiceProfessionalFormset = inlineformset_factory(models.Professional,models.ServiceProfessional, form=ServiceProfessionalForm, extra=1)
ProfessionalCityFormSet = inlineformset_factory(models.Professional,models.ProfessionalCity, form=ProfessionalCityForm, extra=3)
ProfessionalCategoryFormSet = inlineformset_factory(models.Professional,models.ProfessionalCategory, form=ProfessionalCategoryForm, extra=0)

