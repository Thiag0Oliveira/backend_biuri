# -*- coding: utf-8 -*-

from .action import Action
from .exception import RequiredParameters


class Withdraw(Action):

    def list(self, data={}):
        url = self.api.make_url(['withdraw_requests'+'?custom_variables_name=account_id=&custom_variables_value='+data['account_id']])
        print(url)
        return super(Withdraw, self).list(url, data)
