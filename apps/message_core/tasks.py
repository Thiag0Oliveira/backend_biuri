import json
import string

from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .models import PushSchedule, PushToken
from apps.customer.models import Customer
from apps.professional.models import Professional, ServiceProfessional, SaloonScheduleRemove
from datetime import datetime
import time

import requests
from celery import shared_task


class Notification():

    def push(self, to, title, body, data={}, multiple=False):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        url = 'https://exp.host/--/api/v2/push/send'
        if multiple:
            payload = []
            for i in to:
                payload.append({'to': i, 'title': title, 'sound': 'default', 'body': body, 'data': data})
        else:
            payload = {'to': to, 'title': title, 'sound': 'default', 'body': body, 'data': data}
        res = requests.post(url, data=json.dumps(payload), headers=headers)
        return json.loads(res.content.decode('utf-8'))

@shared_task
def send_push_message(to, title, body, data={}):
    headers = { 'Content-Type': 'application/json', 'Accept': 'application/json'}
    url = 'https://exp.host/--/api/v2/push/send'
    payload = {'to': to, 'title': title,'body': body, 'data': data}
    res = requests.post(url, data=json.dumps(payload), headers=headers)
    return json.loads(res.content.decode('utf-8'))

@shared_task
def send_push_message_schedule():
    push_schedules = PushSchedule.objects.filter(has_sended=False, date_schedule__lte=datetime.now())
    for push_schedule in push_schedules:
        push_schedule.has_sended = True
        push_schedule.save()
        users = []
        if push_schedule.send_customer:
            users += list(Customer.objects.all().values_list('user_id', flat=True))
        if push_schedule.send_professional:
            users += list(Professional.objects.all().values_list('user_id', flat=True))
        push_tokens_customers = PushToken.objects.filter(user_id__in=users)
        n = Notification()
        push_text = push_schedule.text
        title = push_schedule.title
        for push_token in push_tokens_customers:
            if push_token.token:
                try:
                    n.push(
                        to=push_token.token,
                        title=title,
                        body=push_text
                    )
                    time.sleep(0.1)
                except:
                    print('erro')
    return 'success'

@shared_task
def reEnableService(id):
    SaloonScheduleRemove.objects.get(pk=id).delete()
    return True