# -*- coding: utf-8 -*-

from .omieapi import default_api


class Action(object):

    def __init__(self):
        self.api = default_api()

    def create(self, url, omie_call, data):
        return self.api.post(url, omie_call, data)

    def search(self, url, omie_call):
        return self.api.get(url, omie_call)

    def change(self, url, omie_call, data):
        return self.api.put(url, omie_call, data)

    def remove(self, url, omie_call):
        return self.api.delete(url)

    def list(self, url, omie_call, data=None):
        if data is None:
            data = {"pagina": 1, "registros_por_pagina": 50, "apenas_importado_api": "N"}
        return self.api.post(url, omie_call, data)
