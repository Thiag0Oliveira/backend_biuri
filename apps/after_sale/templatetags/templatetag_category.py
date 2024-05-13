from collections import OrderedDict
from urllib.parse import urlencode

from django import template
from django.utils.safestring import mark_safe


register = template.Library()

@register.simple_tag
def url_replace(request, field, value, direction=''):
    dict_ = request.GET.copy()

    if field == 'order_by' and field in dict_.keys():
      if dict_[field].startswith('-') and dict_[field].lstrip('-') == value:
        dict_[field] = value
      elif dict_[field].lstrip('-') == value:
        dict_[field] = "-" + value
      else:
        dict_[field] = direction + value
    else:
      dict_[field] = direction + value

    return urlencode(OrderedDict(sorted(dict_.items())))

@register.simple_tag
def arrow_order(request, field, value):
    dict_ = request.GET.copy()
    something = '<i class="material-icons" style="font-color:#fff; font-size: 16px ">{}</i>'
    if field == 'order_by' and field in dict_.keys():
      if dict_[field].startswith('-') and dict_[field].lstrip('-') == value:
        icon = 'arrow_upward'
        return mark_safe(something.format(icon))
      elif dict_[field].lstrip('-') == value:
        icon = 'arrow_downward'
        return mark_safe(something.format(icon))
    return mark_safe('')


@register.filter
def translate_status(value):
    status = {'draft': 'Rascunho',
     'complete_draft': 'Rascunho Completo',
     'flexible_draft': 'Rascunho Flexível',
     'waiting_confirmation': 'Aguardando Confirmação',
              'waiting_payment': 'Aguardando pagamento',
              'waiting_approval': 'Aguardando Confirmação do Cliente',
     'confirmated': 'Confirmado',
     'on_transfer': 'A caminho',
     'waiting_customer': 'Aguardando o Cliente',
     'in_attendance': 'Em atendimento',
     'completed': 'Concluído',
     'canceled': 'Cancelado',
     'canceled_by_customer': 'Cancelado pelo Cliente',
     'canceled_by_professional': 'Cancelado pelo Profissional',
     'expired': 'Expirado',
     'pending_payment': 'Problema no pagamento',
     'scheduling_shock': 'Choque de horário',
     'rejected': 'Rejeitado',
     'flexible_draft': 'Rascunho com Janela'}
    return status[value]

@register.filter
def translate_type(value):
    type = {'': 'Não informado',
            'has_preference': 'Agendando Diretamente',
            'dont_has_preference': 'Peça Já'}
    return type[value]


@register.filter
def translate_transaction_type(value):
    type = {
        'professional': 'Profissional',
        'marketplace': 'Biuri',
        'tax': 'Taxas',
        'executive': 'Executivo',
        'discount': 'Desconto',
        'tax_interest': 'Juros'
    }
    return type[value]


@register.filter
def translate_payment_status(value):
    status = {
        'pending': 'Pendente',
        'processing': 'Processando',
        'accepted': 'Concluído',
        'rejected': 'Rejeitada',
        'refunded': 'Reembolsado'
    }
    return status[value]
