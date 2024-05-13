# -*- coding: utf-8 -*-

from .action import Action
from .exception import RequiredParameters


class Transaction(Action):

    def list(self, data={}):
        url = self.api.make_url(['financial_transaction_requests'])
        return super(Transaction, self).list(url, data)

    def advance(self, data={}):
        url = self.api.make_url(['financial_transaction_requests', 'advance'])
        return super(Transaction, self).create(url, data)
