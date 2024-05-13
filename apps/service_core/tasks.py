import platform
import json
import locale
import calendar
import urllib.parse
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from dateutil.rrule import DAILY, rrule
from django.db.models import Count

import requests
from celery import shared_task

from apps.common.views import Sms
from apps.lead_captation.models import Lead
from apps.message_core.models import PushToken
from apps.professional.models import ProfessionalScheduleDefault, ProfessionalSchedule, Schedule, Professional
from apps.payment.models import Payment

from .models import Attendance, AttendanceService

if (platform.system() != 'Windows'):
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")

@shared_task
def send_push_message(to, title, body, data={}):
    headers = { 'Content-Type': 'application/json', 'Accept': 'application/json'}
    url = 'https://exp.host/--/api/v2/push/send'
    payload = {'to': to, 'title': title,'body': body, 'data': data}
    res = requests.post(url, data=json.dumps(payload), headers=headers)
    return json.loads(res.content.decode('utf-8'))

@shared_task
def send_sms(to, msg):
    sms = Sms()
    data = {'to': str(55) + to, 'from': 'BIURI', 'msg': msg}
    res = sms.send(data=data)
    return json.loads(res.content.decode('utf-8'))

@shared_task
def send_push_attendance(interval=1440):
    attendances = Attendance.objects.filter(scheduling_date__lte= datetime.now() + timedelta(minutes=interval), is_push_notificated=False)
    for attendance in attendances:
        message_professional ="Oi, você tem um atendimento Biuri com {} na {} ({})".format(attendance.customer.user.first_name,attendance.scheduling_date.strftime("%A"), attendance.scheduling_date.strftime("%d/%m/%Y às %H:%M"))
        message_customer ="Oi, você tem um atendimento Biuri com {} na {} ({})".format(attendance.professional.user.first_name,attendance.scheduling_date.strftime("%A"), attendance.scheduling_date.strftime("%d/%m/%Y às %H:%M"))
        customer_tokens = PushToken.objects.filter(user=attendance.customer.user)
        professional_tokens = PushToken.objects.filter(user=attendance.professional.user)
        if professional_tokens:
            for professional_token in professional_tokens:
                send_push_message.delay(
                    to=professional_token.token,
                    title='Biuri',
                    body=message_professional
                )
        if customer_tokens:
            for customer_token in customer_tokens:
                send_push_message.delay(
                    to=customer_token.token,
                    title='Biuri',
                    body=message_customer
                )
    attendances.update(is_push_notificated=True)
    return 'finish'

@shared_task
def send_sms_attendance(interval=121):
    sms = Sms()
    attendances = Attendance.objects.filter(scheduling_date__lte= datetime.now() + timedelta(minutes=interval), is_sms_notificated=False)
    for attendance in attendances:
        message_professional ="Oi, voce tem um atendimento Biuri com {} as {}".format(attendance.customer.user.first_name,attendance.scheduling_date.strftime("%H:%M"))
        message_customer ="Oi, voce tem um atendimento Biuri com {} as {}".format(attendance.professional.user.first_name,attendance.scheduling_date.strftime("%H:%M"))
        if attendance.customer.celphone:
            send_sms.delay(attendance.customer.celphone,message_customer)
        if attendance.professional.celphone:
            send_sms.delay(attendance.professional.celphone,message_professional)
    attendances.update(is_sms_notificated=True)
    return 'finish'

@shared_task
def generate_schedule(month=None, year=None, professional=None):
    today = date.today()
    if month is None and year is None:
        today = today + relativedelta(months=2)
        month = today.month
        year = today.year
    final_day = calendar.monthrange(year,month)[1]
    days = list(rrule(DAILY, dtstart=date(year,month,1), until=date(year,month,final_day)))
    for day in days:
        dayofweek = day.weekday()
        if professional is None:
            professional_schedules = ProfessionalScheduleDefault.objects.filter(day_of_week=dayofweek)
        else:
            professional_schedules = ProfessionalScheduleDefault.objects.filter(day_of_week=dayofweek, professional_id=professional)
        for professional_schedule in professional_schedules:
            professional_schedule_exists = ProfessionalSchedule.objects.filter(professional=professional_schedule.professional,
                                                                               date_schedule=day)
            if not professional_schedule_exists.exists():
                professional_schedule_new = ProfessionalSchedule(
                    professional=professional_schedule.professional,
                    provide_all_day=professional_schedule.provide_all_day,
                    dawn_morning=professional_schedule.dawn_morning,
                    afternoon_night=professional_schedule.afternoon_night,
                    date_schedule=day,
                    dawn_morning_range_begin=professional_schedule.dawn_morning_range_begin,
                    dawn_morning_range_end=professional_schedule.dawn_morning_range_end,
                    afternoon_night_range_begin=professional_schedule.afternoon_night_range_begin,
                    afternoon_night_range_end=professional_schedule.afternoon_night_range_end
                    )
                professional_schedule_new.save()
    return 'finish'

def generate_schedule_professional_new(professional):
    today = date.today()
    generate_schedule(month=today.month, year=today.year, professional=professional)
    today = date.today() + relativedelta(months=1)
    generate_schedule(month=today.month, year=today.year, professional=professional)
    today = date.today() + relativedelta(months=2)
    generate_schedule(month=today.month, year=today.year, professional=professional)
    return 'success'

def regenerate_schedule_professional_new(professional):
    today = date.today()
    schedules_professional = ProfessionalSchedule.objects.filter(professional_id=professional, date_schedule__gte=today).delete()
    schedules = Schedule.objects.filter(professional_id=professional, daily_date__gte=today, attendance__isnull=True).delete()
    generate_schedule_professional_new(professional)
    return 'success'

@shared_task
def expire_attendance(minutes_tolerancy_confirmation, minutes_schedduling_date):
    datetime_tolerancy = datetime.now() + timedelta(minutes=minutes_tolerancy_confirmation)
    schedduling_date_range = datetime.now() + timedelta(minutes=minutes_schedduling_date)
    attendances = Attendance.objects.filter(status='waiting_confirmation', created__lte=datetime_tolerancy,
                                           scheduling_date__lte=schedduling_date_range)
    for attendance in attendances:
        attendance.status = 'expired'
        attendance.save()
    return list(attendances.values_list('pk', flat=True))


@shared_task
def process_executive_leads(executive_id, ddds=[]):
    for ddd in ddds:
        leads = Lead.objects.filter(executive__isnull=True,
                                    telephone__startswith=ddd).update(executive_id=executive_id)

@shared_task
def process_refund():
    p = Payment.objects.filter(status='accepted').filter(attendance__status__in=['canceled_by_customer', 'canceled_by_professional', 'expired', 'rejected', 'scheduling_shock'])
    for i in p:
        i.attendance.refund()

@shared_task
def count_attendances():
    p = Attendance.objects.filter(status='completed', professional__isnull=False).values('professional_id').annotate(y=Count('id', distinct=True))
    for i in p:
        Professional.objects.filter(pk=i['professional_id']).update(attendance_completed_count=i['y'])

@shared_task
def whatsapp_message(text, chat_id=None):
    body = dict()
    body['chatId'] = chat_id if chat_id is not None else '558187666730-1579013519@g.us'
    body['body'] = text
    url = 'https://eu6.chat-api.com/instance4448/message?token=bu9c0ti7u3nkqncc'
    r = requests.post(url=url, data=body)

import hashlib
def encrypt_string(hash_string):
    sha_signature = \
        hashlib.sha256(hash_string.encode()).hexdigest()
    return sha_signature

@shared_task()
def pixel_feedback(attendance_id=None,event_name=None):
    token = 'EAAB9tewZATlwBAOM5S9ZCPiJ8vtudpuRLyzS10XxxxW8Y3UX8OQTkXwnTOlJSKMMvNP5LdiwwDguqR1m8NnbIfvEB3kh0ZAf5pI1IAzC6UN1ZCzE1zOalUdbtAjTT9u2WQiXQspoDAIpbBt4877odtnZBbO4tRtTYPZCJGZBeFqzwC8aJZBsyTtRY93ULHL7fsoZD'
    datetime_pixel = str(round(datetime.now().timestamp()))
    event = {
                'event_name': event_name,
                'event_time': datetime_pixel,
                'user_data': {
                    'em': encrypt_string('ytalo.pigeon@gmail.com')
                },
            }
    if attendance_id is not None:
        attendance = Attendance.objects.get(pk=attendance_id)
        services = AttendanceService.objects.filter(attendance=attendance).select_related('service')
        event['custom_data'] = {'order_id': attendance.pk,
                                'value': float(attendance.total_price),
                                'currency': 'BRL'}
        if services.exists():
            services_list = []
            for service in services:
                services_list.append({'id': service.service.name,'quantity': service.quantity,'item_price': float(service.price)})
            event['custom_data']['contents'] = services_list
        else:
            event['custom_data']['contents'] = [{'id': attendance.initial_service.name,'quantity': 1,'item_price': float(attendance.total_price)}]
        if attendance.customer:
            event['user_data']['em'] = encrypt_string(attendance.customer.user.email)

    data = {
        'data': [
            event
        ],
        'access_token': token
    }
    url_string = urllib.parse.urlencode(data)
    url = "https://graph.facebook.com/v7.0/567095137261762/events?" + url_string
    r = requests.post(url)
    return r.json()