# -*- coding: utf-8 -*-

from .action import Action
from .exception import RequiredParameters


class Cliente(Action):

    def list(self, data=None):
        url = self.api.make_url(['geral/clientes/'])
        omie_call = 'ListarClientes'
        return super(Cliente, self).list(url, omie_call, data)


    def create(self, data):
        url = self.api.make_url(['geral/clientes/'])
        omie_call = 'UpsertCliente'
        return super(Cliente, self).create(url, omie_call, data)