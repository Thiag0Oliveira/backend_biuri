# -*- coding: utf-8 -*-

from .action import Action
from .exception import RequiredParameters
import requests
from requests.auth import HTTPBasicAuth
import json


class MarketPlace(Action):

    def create(self, data={}):
        url = self.api.make_url(['marketplace', 'create_account'])
        return super(MarketPlace, self).create(url, data)

    def request_verification(self, id, data, api_token):
        if not data.get('data', None):
            raise RequiredParameters('MarketPlace data not informed')
        url = self.api.make_url(['accounts', id, 'request_verification'])
        headers = {"Content-Type": "application/json",
            "Accept": "application/json"}
        response = requests.request('POST', url,
                                    auth=HTTPBasicAuth(api_token, ''),
                                    data=json.dumps(data),
                                    headers=headers)
        return json.loads(response.content.decode('utf-8'))

    def update_bank_data(self, id, data, api_token):
        # if not data.get('data', None):
        #     raise RequiredParameters('MarketPlace data not informed')
        url = self.api.make_url(['bank_verification'])
        headers = {"Content-Type": "application/json",
            "Accept": "application/json"}
        print(json.dumps(data))
        response = requests.request('POST', url,
                                    auth=HTTPBasicAuth(api_token, ''),
                                    data=json.dumps(data),
                                    headers=headers)
        return json.loads(response.content.decode('utf-8'))

    def sub_account(self, id):
        url = self.api.make_url(['accounts', id])
        return super(MarketPlace, self).list(url)
