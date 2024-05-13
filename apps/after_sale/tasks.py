import json
from datetime import datetime, timedelta, date
from dateutil.rrule import DAILY, rrule

import requests
from celery import shared_task
from django.db.models import Count

from apps.common.views import Sms
from .models import Task
from apps.service_core.models import Attendance
from apps.customer.models import Customer
from apps.professional.models import Professional

# from apps.after_sale.tasks import *
# after_sale_process()

@shared_task
def after_sale_process_satisfacao(days=45, customers_satisfacao=7, professionals_satisfacao=7):
    date_initial = datetime.today() - timedelta(days=days)
    tasks_users = Task.objects.filter(created__date__gte=date_initial)
    tasks_users_list = tasks_users.filter(user__isnull=False).values_list('user', flat=True)
    customers_users = Customer.objects.filter(celphone__isnull=False).exclude(
        user__in=tasks_users_list)[:customers_satisfacao]
    professionals_users = Professional.objects.filter(celphone__isnull=False).exclude(
        user__in=tasks_users_list)[:professionals_satisfacao]
    for customers_user in customers_users:
        task = Task(user=customers_user.user, type='Cliente', reason='Pesquisa de satisfação',
                    description='Pesquisa de satisfação com cliente')
        task.save()
    for professionals_user in professionals_users:
        task = Task(user=professionals_user.user, type='Profissional', reason='Pesquisa de satisfação',
                    description='Pesquisa de satisfação com profissional')
        task.save()
    return 'success'

@shared_task
def after_sale_first_attendance():
    attendances_tasks = Task.objects.filter(attendance__isnull=False).values_list('attendance', flat=True)
    attendances = Attendance.objects.select_related('customer__user', 'professional__user').filter(
        scheduling_date__date=datetime.today(), status='completed')
    attendances_customers = Attendance.objects.values('customer__user').annotate(attendances_count=Count('pk'))\
               .filter(attendances_count=1).values_list('customer__user', flat=True)
    attendances_professional = Attendance.objects.values('professional__user').annotate(
        attendances_count=Count('pk')) \
        .filter(attendances_count=1).values_list('professional__user', flat=True)
    attendances_customer_first_attendance = list(attendances.filter(customer__user__in=attendances_customers))
    attendances_professional_first_attendance = list(attendances.filter(professional__user__in=attendances_professional))
    for attendance in attendances_customer_first_attendance:
        task = Task(user=attendance.customer.user, attendance=attendance, type='Cliente', reason='Primeiro Atendimento',
                    description='Primeiro Atendimento')
        task.save()
    for attendance in attendances_professional_first_attendance:
        task = Task(user=attendance.professional.user, attendance=attendance, type='Profissional', reason='Primeiro Atendimento',
                    description='Pesquisa de satisfação com profissional')
        task.save()
    return 'success'

@shared_task
def after_sale_cancelation_by_professional(attendance):
    task = Task(user=attendance.customer.user, attendance=attendance, type='Cliente',
                reason='Cancelamento', description='Cancelamento realizado pelo profissional')
    task.save()
    msg = "Cancelamento: Atendimento: {} Cliente: {} Celular: {} Servico: {} Horario: {}".format(
        attendance.pk,attendance.customer.user.first_name,attendance.customer.celphone,
        attendance.initial_service, str(attendance.scheduling_date))
    data = {'to': str(55) + str(81987666730), 'from': 'BIURI', 'msg': msg}
    sms = Sms()
    sms.send(data=data)
    return 'success'
