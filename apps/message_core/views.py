import requests
import json
from django.shortcuts import render


# Create your views here.


def slack_message(text):
    url = 'https://hooks.slack.com/services/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'
    data = {'text': text}
    r = requests.post(url, data=json.dumps(data))
    return r