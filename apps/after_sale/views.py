from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.views import generic
from django.db import transaction
from django.db.models import Q

from decimal import Decimal

# Create your views here.
from apps.after_sale.forms import AttendanceForm, AttendanceServiceForm
from apps.professional.models import Executive, Professional, ProfessionalCity, ServiceProfessional
from apps.service_core.models import Attendance, AttendanceService, Service
from apps.payment.models import Transaction, Voucher
from apps.common.views import GenericFilterList
from apps.core.models import City

from .filters import GenericFilter

class AttendanceList(GenericFilterList, generic.ListView):
    """
    Lists Attendances(:model:`service_core.Attendance`)
    """
    model = Attendance
    queryset = Attendance.objects.all()
    template_name = 'attendance/attendance_list.html'
    paginate_by = 20
    ordering = '-id'
    filterset_class = GenericFilter
    template_filter_name = 'attendance_filter.html'
    verbose_name = 'Attendance'
    verbose_name_plural = 'Attendances'

    def get_ordering(self):
        ordering = self.request.GET.get('order_by', self.ordering)
        return ordering

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.has_perm('service_core.change_attendance'):
            return super(AttendanceList, self).dispatch(request, *args, **kwargs)
        return HttpResponseNotFound('<h1>Page not found</h1>')

    def get_queryset(self):
        queryset = super(AttendanceList, self).get_queryset().select_related('customer__user','initial_service','professional__user')
        query_params = self.request.GET.dict()
        user_executive = self.user_executive()
        if user_executive is not None:
            professional_executive = Professional.objects.filter(user=self.request.user)[0]
            professional_citys = ProfessionalCity.objects.filter(professional=professional_executive.pk).values('city')
            cities = City.objects.filter(pk__in=professional_citys).values_list('name', flat=True)
            cities = list(cities)
            queryset = queryset.filter(Q(professional__executive=user_executive) | Q(address__city__iregex= r'(' + '|'.join(cities) + ')', professional=None))
        if 'status' in query_params:
            if query_params['status'] != '':
                queryset = queryset.filter(status=query_params['status'])
        if 'id' in query_params:
            if query_params['id'] != '':
                queryset = queryset.filter(pk=query_params['id'])
        if 'q' in query_params:
            q = query_params['q']
            if q != '':
                queryset = queryset.filter(Q(professional__celphone=q)|Q(customer__celphone=q)|Q(professional__user__first_name__icontains=q)|Q(customer__user__first_name__icontains=q))
        if 'voucher' in query_params:
            voucher = query_params['voucher']
            if voucher != '':
                queryset = queryset.filter(voucher__code__icontains=voucher)
        return queryset


class AttendanceDetail(generic.DetailView):
    """
    Displays the details of a given Attendance(:model:`service_core.Attendance`)
    """
    model = Attendance
    queryset = Attendance.objects.select_related()
    template_name = 'attendance/attendance_detail.html'

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.has_perm('service_core.change_attendance'):
            return super(AttendanceDetail, self).dispatch(request, *args, **kwargs)
        return HttpResponseNotFound('<h1>Page not found</h1>')



class AttendanceUpdate(generic.UpdateView):
    """
    View for Attendance(:model:`service_core.Attendance`) update
    """
    model = Attendance
    queryset = Attendance.objects.select_related()
    template_name = 'attendance/after_sale_attendance_form.html'
    form_class = AttendanceForm
    # attendance_services_form = modelformset_factory(AttendanceService, form=AttendanceServiceForm,
    #                                                   extra=0)

    def get_success_url(self):
        url = '/after_sale/attendance/' + str(self.object.pk) + '/update'
        return url

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.has_perm('service_core.change_attendance'):
            return super(AttendanceUpdate, self).dispatch(request, *args, **kwargs)
        return HttpResponseNotFound('<h1>Page not found</h1>')

    def get_context_data(self, **kwargs):
        executive = self.user_executive()
        context = super(AttendanceUpdate, self).get_context_data(**kwargs)
        # context['service_formset'] = self.attendance_services_form(prefix='service_formset', queryset=AttendanceService.objects.filter(attendance=self.object))
        context['form'].fields['professional'].queryset = context['form'].fields['professional'].queryset.all()
        if executive is not None:
            context['form'].fields['professional'].queryset = context['form'].fields['professional'].queryset.filter(executive=executive)
        return context

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    # @transaction.atomic
    # def post(self, request, *args, **kwargs):
    #     self.object = self.get_object()
    #     context = {}
    #     form = self.form_class(request.POST, instance=self.object)
    #     context['form'] = form
    #     attendance_services_formset = self.attendance_services_form(request.POST, prefix='service_formset')
    #     context['service_formset'] = attendance_services_formset
    #     if form.is_valid() and attendance_services_formset.is_valid():
    #         form.save()
    #         for attendance_service_form in attendance_services_formset:
    #             attendance_service_form = attendance_service_form.save(commit=False)
    #             attendance_service_form.attendance = self.object
    #             attendance_service_form.save()
    #         return super(AttendanceUpdate, self).form_valid(form)
    #     return render(request, self.template_name, context)


class TransactionList(generic.ListView):
    """
    Lists Transactions(:model:`payment.Transaction`)
    """
    model = Transaction
    queryset = Transaction.objects.select_related('attendance','attendance__professional__user', 'transfer__professional__user')
    template_name = 'attendance/transaction_list.html'
    # paginate_by = 10
    ordering = '-id'

    def get_ordering(self):
        ordering = self.request.GET.get('order_by', self.ordering)
        return ordering

    def user_executive(self):
        executive = Executive.objects.filter(user=self.request.user)
        if executive.exists():
            return executive[0]
        return None

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.has_perm('service_core.change_attendance'):
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseNotFound('<h1>Page not found</h1>')

    def get_queryset(self):
        queryset = super().get_queryset().filter(type__in=['executive','professional','discount'])\
            .select_related('attendance', 'attendance__professional', 'attendance__voucher')
        query_params = self.request.GET.dict()
        user_executive = self.user_executive()
        if user_executive is not None:
            queryset = queryset.filter(Q(attendance__professional__executive=user_executive)|Q(transfer__professional__executive=user_executive))
        else:
            queryset = queryset.filter(Q(attendance__professional__executive_id=2) | Q(
                transfer__professional__executive=2))
        if 'initial_date' in query_params:
            if query_params['initial_date'] != '':
                queryset = queryset.filter(created__date__gte=query_params['initial_date'])
        if 'final_date' in query_params:
            if query_params['final_date'] != '':
                queryset = queryset.filter(created__date__lte=query_params['final_date'])
        if 'types' in query_params:
            if query_params['types'] != '':
                queryset = queryset.filter(type__in=self.request.GET.getlist('types'))
        if 'is_recebido' in query_params:
            if query_params['is_recebido'] != '':
                queryset = queryset.filter(is_recebido=query_params['is_recebido'])
        return queryset


def get_voucher(request):
    """
    Returns Voucher data for Attendance update
    """
    voucher_id = request.GET.get('voucher_id')
    voucher = Voucher.objects.filter(code=voucher_id)[0]
    if voucher.discount_type == 'percent':
        discount = voucher.discount
    else:
        discount = voucher.discount_value
    discount = Decimal(discount)
    data = {
        'discount': discount,
        'discount_type': voucher.discount_type
    }
    return JsonResponse(data)

def update_price(request):
    """
    Returns the total price of a given Attendance
    """
    discount = request.GET.get('discount')
    attendance_id = request.GET.get('attendance')
    attendance = Attendance.objects.filter(pk=attendance_id)[0]
    total = attendance.total_price - Decimal(discount)
    data = {
        'total': total,
    }
    return JsonResponse(data)



def attendance_service_delete(request):
    """
    Deletes the chosen Service in the current Attendance
    """
    pk = request.POST.get('pk')
    attendance_service = AttendanceService.objects.get(id=pk)
    attendance_service.delete()
    return JsonResponse(status=200, data={})


def attendance_service_edit(request):
    """
    Allows the user to edit the chosen Service in the current Attendance
    """
    pk = request.POST.get('pk')
    price = request.POST.get('price')
    duration = request.POST.get('duration')
    attendance_service = AttendanceService.objects.get(id=pk)
    attendance_service.price = price.replace(",", ".")
    attendance_service.duration = duration
    attendance_service.save()
    return JsonResponse(status=200, data={})


def get_attendance_service(request):
    """
    Lists the Services in the current Attendance
    """
    pk = request.GET.get('pk')
    attendance_services = AttendanceService.objects.filter(attendance_id=pk)
    attendance_service_list = []
    for attendance_service in attendance_services:
        attendance_service_list.append({'id': attendance_service.id, 'service': attendance_service.service.name, 'price': attendance_service.price, 'duration': attendance_service.duration})
    data = {
        "attendance_services": attendance_service_list,
    }
    return JsonResponse(status=200, data=data)


def get_services(request):
    """
    Lists the Services available for the current attendance
    """
    # select related to professional
    # professional_id = request.GET.get('professional_id')
    # professional = Professional.objects.get(id=professional_id)
    # professional_services = ServiceProfessional.objects.filter(professional=professional).values_list('service', flat=True)
    # services = Service.objects.filter(id_in=professional_services)
    services = Service.objects.all().order_by('category')
    service_list = []
    for service in services:
        service_list.append({'id': service.id, 'name': service.name})
    data = {
        "services": service_list,
    }
    return JsonResponse(status=200, data=data)


def create_attendance_service(request):
    """
    Creates no Attendance Service object for an Attendance
    """
    attendance_id = request.POST.get('attendance_id')
    service_id = request.POST.get('service_id')
    price = request.POST.get('price')
    duration = request.POST.get('duration')
    attendance = Attendance.objects.get(id=attendance_id)
    service = Service.objects.get(id=service_id)
    new_attendance_service = AttendanceService(attendance=attendance, service=service, price=price.replace(",", "."), duration=duration)
    new_attendance_service.save()
    return JsonResponse(status=200, data={})