# -*- coding: utf-8 -*-

import json
import os
import re

from django.conf import settings

import requests
from requests.auth import HTTPBasicAuth

from .exception import ConfigError


class OmieApi(object):

    def __init__(self, **kwargs):
        self.app_key = kwargs.get("app_key")
        self.app_secret = kwargs.get("app_secret")

    def headers(self):
        return {
            "Content-Type": "application/json"
        }

    def base_request(self, url, method, omie_call, data={}):
        try:
            data = {"call": omie_call,
                    "app_key": self.app_key,
                    "app_secret": self.app_secret,
                    "param": [data]
                    }
            response = requests.request(method, url,
                                        data=json.dumps(data),
                                        headers=self.headers())
            return json.loads(response.content.decode('utf-8'))
        #TODO: Create especifics exceptions
        except Exception as error:
            raise

    def get(self, url, omie_call, data={}):
        return self.base_request(url, 'GET', omie_call, data=data)

    def post(self, url, omie_call, data={}):
        return self.base_request(url, 'POST', omie_call, data=data)

    def put(self, url, omie_call, data={}):
        return self.base_request(url, 'PUT', omie_call, data=data)

    def delete(self, url, omie_call):
        return self.base_request(url, 'DELETE', omie_call)

    def make_url(self, paths):
        url = 'https://app.omie.com.br/api/v1'
        for path in paths:
            url = re.sub(r'/?$', re.sub(r'^/?', '/', str(path)), url)
        return url

__default_api__ = None


def default_api():

    global __default_api__
    if __default_api__ is None:
        try:
            app_key = settings.APP_OMIE_KEY
            app_secret = settings.APP_OMIE_SECRET
        except KeyError:
            raise ConfigError("Required IUGU_API_TOKEN")
        __default_api__ = OmieApi(app_key=app_key,app_secret=app_secret)
    return __default_api__


def config(**kwargs):

    global __default_api__
    __default_api__ = OmieApi(app_key=settings.APP_OMIE_KEY,app_secret=settings.APP_OMIE_SECRET)
    return __default_api__
