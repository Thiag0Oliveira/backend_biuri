import datetime
import json
import time

from django.contrib.auth.models import User
from django.shortcuts import render

import requests
import numpy as np

# Create your views here.


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
        try:
            res = requests.post(url, data=json.dumps(payload), headers=headers)
            return json.loads(res.content.decode('utf-8'))
        except Exception as e:
            print(e)
            try:
                time.sleep(2)
                res = requests.post(url, data=json.dumps(payload), headers=headers)
                return json.loads(res.content.decode('utf-8'))
            except Exception as e:
                print(e)
                time.sleep(2)
                res = requests.post(url, data=json.dumps(payload), headers=headers)
                return json.loads(res.content.decode('utf-8'))