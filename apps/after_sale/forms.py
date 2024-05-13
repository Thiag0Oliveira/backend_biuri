from django import forms
from django.db.models import F, Q
from apps.service_core.models import Attendance, AttendanceService, Service, Voucher
from apps.professional.models import Professional, Executive
from apps.payment.models import CreditCard
from datetime import datetime


class AttendanceForm(forms.ModelForm):

    class Meta:
        model = Attendance
        fields = ['scheduling_date', 'professional', 'status', 'voucher', 'total_discount', 'credit_card']

    def __init__(self, *args, **kwargs):
        super(AttendanceForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        self.fields['total_discount'].widget.attrs['class'] = 'form-control'
        self.fields['voucher'].queryset = Voucher.objects.filter(initial_date__lte=datetime.now(), final_date__gte=datetime.now()).exclude(quantity=F('quantity_used'), has_used=False)
        if instance.professional is not None:
            self.fields['professional'].queryset = Professional.objects.filter(Q(professional_enabled=True,professional_enabled_executive=True,\
                                                                               services__service=instance.initial_service, services__is_removed=False)|\
                                                                               (Q(pk=instance.professional.pk)))\
                .select_related('user').distinct().order_by('full_name')
        
        self.fields['credit_card'].queryset = CreditCard.objects.filter(customer=self.instance.customer)
            # .filter(services__service=instance.initial_service, services__is_removed=False,
            #         citys__city__name=instance.address.city).order_by('full_name')

class AttendanceServiceForm(forms.ModelForm):

    class Meta:
        model = AttendanceService
        fields = ['service', 'price', 'duration']

    def __init__(self, *args, **kwargs):
        super(AttendanceServiceForm, self).__init__(*args, **kwargs)
        self.fields['service'].queryset = Service.objects.filter(is_app_enabled=True).order_by('name')
