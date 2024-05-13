from datetime import date, datetime, timedelta

import pandas as pd
from django.db.models import Count
from django.http import JsonResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, View

from dateutil.relativedelta import relativedelta
from io import BytesIO as IO

from apps.common.views import ModelMetric
from apps.customer.models import Customer
from apps.professional.models import Executive, Professional, ProfessionalEvaluation
from apps.service_core.models import Attendance


# Create your views here.

class DashboardHome(View):
    """
    View for the Dashboard home
    """
    template_name = "dashboard.html"

    def get(self, request,*args, **kwargs):
        context = {}
        model_metric = ModelMetric()
        professional_query = Professional.objects.all()
        professional_enabled_query = Professional.objects.filter(professional_enabled=True)
        customer_query = Customer.objects.all()
        attendance_query = Attendance.objects.all()
        evaluation_query = ProfessionalEvaluation.objects.all()
        executive_query = Executive.objects.all()
        executive = Executive.objects.filter(user=self.request.user)
        if executive and not self.request.user.is_superuser:
            executive = executive[0]
            professional_query = professional_query.filter(executive=executive)
            professional_enabled_query = professional_enabled_query.filter(executive=executive)
            attendance_query = attendance_query.filter(professional__executive=executive)
            evaluation_query = evaluation_query.filter(professional__executive=executive)
            attendance_customer_query = attendance_query.values_list('customer')
            customer_query = customer_query.filter(pk__in=attendance_customer_query)
        else:
            professional = Professional.objects.filter(user=self.request.user)
            if professional:
                professional = professional.first()
                context['is_professional'] = True
                attendance_query = attendance_query.filter(professional=professional)
                evaluation_query = evaluation_query.filter(professional=professional)
                attendance_customer_query = attendance_query.values_list('customer')
                customer_query = customer_query.filter(pk__in=attendance_customer_query)
        context['professional'] = model_metric.get_all_metrics(professional_query)
        context['professional_enabled'] = model_metric.get_all_metrics(professional_enabled_query)
        context['executive'] = model_metric.get_all_metrics(executive_query)
        context['customer'] = model_metric.get_all_metrics(customer_query)
        context['attendance'] = model_metric.get_all_metrics(attendance_query)
        context['evaluation'] = model_metric.get_all_metrics(evaluation_query)
        context['status_attendance'] = model_metric.get_status_metrics(attendance_query, ['draft',
                                                                                          'waiting_confirmation',
                                                                                          'confirmated', 'on_transfer',
                                                                                          'waiting_customer',
                                                                                          'in_attendance', 'completed',
                                                                                          'expired',
                                                                                          'canceled_by_customer',
                                                                                          'canceled_by_professional',
                                                                                          'pending_payment'])
        context['attendance_ranking'] = model_metric.ranking(attendance_query,5)
        return render(request,self.template_name,context)


class FormsExample(TemplateView):
    """
    Example Form
    """
    template_name = "forms.html"

class RelatorioProfissionais(View):
    """

    """
    def get(self, request,*args, **kwargs):
        professionals = Professional.objects.filter(professional_enabled=True, citys__neighborhoods__is_removed=False).values(
            'citys__neighborhoods__description', 'categorys__services__name').annotate(y=Count('id', distinct=True))
        PandasDataFrame = pd.pivot_table(pd.DataFrame(data=list(professionals)), values='y', index=['citys__neighborhoods__description'],
                       columns=['categorys__services__name'])
        sio = IO()
        PandasWriter = pd.ExcelWriter(sio, engine='xlsxwriter')
        PandasDataFrame.to_excel(PandasWriter, sheet_name='Bairros vs Servicos')
        PandasWriter.save()
        sio.seek(0)
        response = StreamingHttpResponse(sio.read(),
                                         content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=%s' % 'excel.xlsx'
        return response