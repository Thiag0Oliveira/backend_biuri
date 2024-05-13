import json
import random
import string
from datetime import date, datetime, timedelta

from django.conf import settings
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.template.loader import get_template
from django.utils.text import slugify

import requests
from dateutil.relativedelta import relativedelta
from django_filters.views import FilterView

from xhtml2pdf import pisa
import os
import hashlib
from twilio.rest import Client


# Create your views here.

class GenericFilterList(FilterView):
    template_name_suffix = '_list'
    model = None
    template_filter_name = None
    filterset_class = None
    list_display = None
    verbose_name = None
    verbose_name_plural = None

    def get_context_data(self, **kwargs):
        context = super(GenericFilterList, self).get_context_data(**kwargs)  # get the default context data
        if self.template_filter_name:
            context['template_filter_name'] = self.template_filter_name  # add extra field to the context
        if self.model:
            if self.verbose_name:
                context['verbose_name'] = self.verbose_name
            else:
                context['verbose_name'] = self.model._meta.verbose_name
            if self.verbose_name_plural:
                context['verbose_name_plural'] = self.verbose_name_plural
            else:
                context['verbose_name_plural'] = self.model._meta.verbose_name_plural
            if self.list_display:
                list_display_names = []
                for field in self.list_display:
                    try:
                        verbose_name = self.model._meta.get_field(field).verbose_name
                    except:
                        verbose_name = field
                    list_display_names.append(verbose_name)
                context['list_display_names'] = list_display_names  # add extra field to the context
        return context


class AjaxableResponseMixin:
    """
    Mixin to add AJAX support to a form.
    Must be used with an object-based FormView (e.g. CreateView)
    """
    def form_invalid(self, form):
        response = super().form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        # We make sure to call the parent's form_valid() method because
        # it might do some processing (in the case of CreateView, it will
        # call form.save() for example).
        response = super().form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response

def get_address(cep):
    # request = requests.get(
    #     'http://www.cepaberto.com/api/v3/cep?cep=' + cep,
    #     headers={'Authorization': 'Token token=48db6779a48984ef7642d30a5fb5180c'})
    # response = request.json()
    # response['cidade'] = response['cidade']['nome']
    # response['estado'] = response['estado']['sigla']
    # response['logradouro'] = response['logradouro'].split(',')[0]
    request = requests.get('https://viacep.com.br/ws/{}/json/'.format(cep))
    response = request.json()
    response_data = {
        'logradouro': response['logradouro'],
        'cidade': response['localidade'],
        'bairro': response['bairro'],
        'estado': response['uf'],
    }
    return JsonResponse(response_data, status=request.status_code)


def get_cep_json(request):
    if request.method == 'GET':
        response = get_address(request.GET.get('cep'))
    return response



class ModelMetric():

    def get_metric(self,queryset,range):
        response = int()
        if range == 'today':
            response = queryset.filter(created__date=datetime.now().date()).count()
        if range == 'yesterday':
            date_metric = (datetime.now() - timedelta(days=1)).date()
            response = queryset.filter(created__date=date_metric).count()
        if range == 'last_week':
            date_metric = (datetime.now() - timedelta(weeks=1)).date()
            response = queryset.filter(created__date__gte=date_metric).count()
        if range == 'last_month':
            date_metric = (datetime.now() - relativedelta(months=1)).date()
            response = queryset.filter(created__date__gte=date_metric).count()
        if range == 'last_year':
            date_metric = (datetime.now() - relativedelta(year=1)).date()
            response = queryset.filter(created__date__gte=date_metric).count()
        return response

    def get_all_metrics(self, queryset):
        response = {}
        list_metrics = ['today', 'yesterday','last_week','last_month','last_year']
        for metric in list_metrics:
            response[metric] = self.get_metric(queryset,metric)
        response['all'] = queryset.count()
        return response

    def get_status_metrics(self, queryset, status_list):
        response = []
        for status in status_list:
            response.append({'name': status, 'metrics': self.get_all_metrics(queryset.filter(status=status))})
        return response

    def ranking(self, queryset, value):
        return queryset.order_by('-modified')[:value]

def generator_code(size=4, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

class Sms(object):
    def __init__(self, token=settings.SMS_TOKEN):
        self.token = token
        # Gerar token no linux echo -n conta:senha | base64

    def headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'Basic %s' % self.token,
            'Accept': 'application/json'
        }

    # def send(self, data={}, multiple=False):
    #     if multiple:
    #         url = "https://api-messaging.movile.com/v1/send-bulk-sms"
    #         payload = {}
    #         payload['messages'] = []
    #         for i in data:
    #             payload['messages'].append({"destination": i['to'] , "messageText": i['from'] + i['msg']})
    #     else:
    #         url = "https://api-messaging.movile.com/v1/send-sms"
    #         payload = {"destination": data['to'] , "messageText": data['from'] + data['msg']}
    #     headers = {
    #         'username': "BIURI MARKETPLACE LTDA",
    #         'authenticationtoken': 'exRD9u4aQdesmxgqw35ug8RhW2op9BdxMz28VTKS',
    #         'content-type': "application/json"
    #     }
    #     response = requests.post(url, data=json.dumps(payload), headers=headers)
    #     return response

    def send(self, data={}, multiple=False):
        # if multiple:
        #     url = "https://api-messaging.movile.com/v1/send-bulk-sms"
        #     payload = {}
        #     payload['messages'] = []
        #     for i in data:
        #         payload['messages'].append({"destination": i['to'] , "messageText": i['from'] + i['msg']})
        # else:
        #     url = "https://api-messaging.movile.com/v1/send-sms"
        #     payload = {"destination": data['to'] , "messageText": data['from'] + data['msg']}
        # headers = {
        #     'username': "BIURI MARKETPLACE LTDA",
        #     'authenticationtoken': 'exRD9u4aQdesmxgqw35ug8RhW2op9BdxMz28VTKS',
        #     'content-type': "application/json"
        # }
        # response = requests.post(url, data=json.dumps(payload), headers=headers)

        account_sid = 'AC945fa9d8248d0fc1bd502bd59223b942'
        auth_token = '938eaa784f5b48c177a99bdda2082e6f'
        client = Client(account_sid, auth_token)

        message = client.messages \
            .create(
            body= data['from'] + ": " + data['msg'],
            from_='+12058721947',
            to='+' + data['to']
        )
        return message


class PermissionView(object):
    permission_required = ''
    prefix_permission = ''

    def get_permission(self, *args, **kwargs):
        if self.permission_required == '':
            return self.model._meta.app_label + '.' + self.prefix_permission + '_' + str(self.model._meta.model_name).lower()
        return self.permission_required

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if not user.has_perm(self.get_permission()):
            raise Http404('Você não tem permissão')
        return super(PermissionView, self).dispatch(request, *args, **kwargs)


class PermissionCreateView(PermissionView):
    prefix_permission = 'add'


class PermissionUpdateView(PermissionView):
    prefix_permission = 'change'


class PermissionListView(PermissionView):
    prefix_permission = 'list'


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    # use short variable names
    sUrl = settings.STATIC_URL      # Typically /static/
    sRoot = settings.STATIC_ROOT    # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL       # Typically /static/media/
    mRoot = settings.MEDIA_ROOT     # Typically /home/userX/project_static/media/

    # convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path


def render_pdf_view(request, template_path, context, filename='report'):
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename=' + filename + '.pdf'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context=context)

    # create a pdf
    pisaStatus = pisa.CreatePDF(
       html, dest=response, link_callback=link_callback)
    # if error then show some funy view
    if pisaStatus.err:
       return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


def slug_generator(seed):
    m = hashlib.md5()
    m.update(seed.encode('utf-8'))
    return slugify(m.hexdigest())

