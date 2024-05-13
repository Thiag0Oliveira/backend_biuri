import json
from datetime import date, datetime, time, timedelta
from decimal import Decimal
import unidecode
from dateutil import parser


from django.contrib.auth.models import User, update_last_login
from django.utils import timezone

from django.db.models import Count, F, Q, Sum
from django.dispatch import Signal
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _

import requests
from allauth.account.utils import filter_users_by_email
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from dateutil import rrule
from django.views import View
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django_filters.rest_framework import DjangoFilterBackend
from oauth2_provider.contrib.rest_framework import TokenHasReadWriteScope
from oauth2_provider.models import AccessToken, Application, get_access_token_model
from oauth2_provider.settings import oauth2_settings
from oauth2_provider.views.mixins import OAuthLibMixin
from oauthlib import common
from rest_auth.registration.views import RegisterView, SocialLoginView
from rest_framework import filters, generics, pagination, status, viewsets
from rest_framework.authtoken.models import Token as Auth_Token
from rest_framework.parsers import FileUploadParser, JSONParser, BaseParser
from rest_framework.views import APIView, Response
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from apps.common.models import UserAddress
from apps.message_core.tasks import reEnableService
from apps.common.views import Sms, generator_code, get_address
from apps.core.models import State, City, Neighborhood
from apps.customer.models import Customer, PricingCriterionCustomer
from apps.dashboard.models import ProfessionalVisualisation
from apps.iugu.token import Token
from apps.lead_captation.models import ExecutiveLead
from apps.message_core.models import News, PushToken
from apps.payment.models import BankAccount, Transaction, Voucher, VoucherCustomer, Transfer
from apps.payment.models import CreditCard as Card
from apps.professional.models import (
    Calendar, EvaluationCustomer, EvaluationType, FavoriteProfessional,
    Professional, ProfessionalEvaluation, ProfessionalSchedule, Schedule,
    ServiceProfessionalPricingCriterion, Executive, SaloonScheduleRemove,)
from apps.professional.views import process_scheduling_shock_calendar
from apps.service_core.models import (
    Attendance, AttendanceService, Category, PricingCriterion, PricingCriterionOptions, Service,
    ServiceProfessional, AttendanceProfessionalConfirmation,
    CancelationReason, AttendanceCancelation)
from apps.service_core.tasks import pixel_feedback
from . import serializers
from .pagination import LastAttendancesPagination


app_authorized = Signal(providing_args=["request", "token"])


class CustomPageNumberPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'pagination': {
                'actual_page': self.page.number,
                'last_page': self.page.paginator.num_pages,
                'has_next': self.page.has_next(),
                'has_previous': self.page.has_previous(),
                'start_index': self.page.start_index(),
                'end_index': self.page.end_index(),
            },
            'results': data
        })


class BestPraticsList(object):
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    filter_fields = '__all__'
    ordering_fields = '__all__'
    pagination_class = CustomPageNumberPagination


class ExecutiveLeadList(BestPraticsList, generics.ListCreateAPIView):
    """
    Lists Executive Leads
    """
    queryset = ExecutiveLead.objects.all()
    serializer_class = serializers.ExecutiveLeadSerializer
    search_fields = ('email',)
    ordering = 'id'


class ExecutiveLeadDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Returns the Detaials, Update and Delete of an Executive Lead
    """
    queryset = ExecutiveLead.objects.all()
    serializer_class = serializers.ExecutiveLeadSerializer


# noinspection PyUnusedLocal
class ResetPassword(APIView):
    """
    Allows Password Reset in the Customer App
    """

    serializer_class = serializers.ResetPasswordSerializer

    # noinspection PyUnusedLocal
    def get(self, request, format=None):
        serializer = self.serializer_class
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(request)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SignUp(RegisterView, OAuthLibMixin):
    """
    Creates an User and Customer objects for new users in the App
    """
    serializer_class = serializers.SignUpSerializer
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        customer = Customer(user=user).save()
        print("Entramos no create")
        if hasattr(request.data, "_mutable"):
            request.data._mutable = True
        request.data.update({"password": request.data['password1']})
        body, status = oauth2_login(self, request, serializer)
        return Response(json.loads(body),
                        status=status,
                        headers=headers)


class Login(OAuthLibMixin, generics.GenericAPIView):
    """
    Login Api for the Apps
    """
    serializer_class = serializers.LoginSerializer
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    def get(self, request, format=None):
        serializer = serializers.LoginSerializer()
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            body, status = oauth2_login(self, request, serializer)
            if status != 400:
                body = json.loads(body)
            return Response(body, status=status)
        if 'email' in serializer.errors:
            body = '{"error": "%s", "status": "%s"}' % (serializer.errors["email"][-1], 'error')
        else:
            body = '{"error": "%s", "status": "%s"}' % (serializer.errors["error"][-1],
                                                        serializer.errors["status"][-1])
        body = json.loads(body)
        return Response(body, status=400)


def oauth2_login(self, request, serializer):
    if hasattr(request.data, "_mutable"):
        request.data._mutable = True
    email = serializer.data['email']
    is_professional = False
    if 'professional' in serializer.data:
        is_professional = serializer.data['professional']
    if is_professional:
        professional = Professional.objects.filter(user__email__iexact=email.lower())
        user = professional[0].user
    else:
        customer = Customer.objects.filter(user__email__iexact=email.lower())
        user = customer[0].user
    update_last_login(None, user)
    app = Application.objects.all()[0]
    request.data.update({"grant_type": "password", "username": user.username,
                         "client_id": app.client_id, "client_secret": app.client_secret})
    url, headers, body, status = self.create_token_response(request)
    if status == 200:
        access_token = json.loads(body).get("access_token")
        if access_token is not None:
            token = get_access_token_model().objects.get(
                token=access_token)
            app_authorized.send(
                sender=self, request=request,
                token=token)
    response = HttpResponse(content=body, status=status)
    for k, v in headers.items():
        response[k] = v
    if 'error' in body:
        status = 400
        body = {'error': 'Usuário ou senha não conferem', 'status': 'error'}
    body = json.dumps(body, ensure_ascii=False)
    return json.loads(body), status


class SendPushNotification(APIView):
    """
    Sends Push Notification to either App
    """
    def post(self, request, format=None):
        serializer = serializers.NotificationSerializer(data=request.data)
        message = {}

        if serializer.is_valid():
            headers = {'Content-Type': 'applications/json', 'Accept': 'applications/json'}
            url = 'https://exp.host/--/api/v2/push/send'

            payload = json.dumps({
                'to': 'ExponentPushToken[%s]' % (serializer.data['to']),
                'title': serializer.data['title'],
                'body': serializer.data['body']
            })
            response = requests.post(url, data=payload, headers=headers)
            if response.status_code >= 200 and response.status_code < 300:
                message = {'status': 'success', 'message': 'Notification sended'}
                return Response(message, status.HTTP_200_OK)
            else:
                return Response(response, status.HTTP_400_BAD_REQUEST)
        return Response(message, status.HTTP_400_BAD_REQUEST)


class FacebookLogin(SocialLoginView):
    """
    App login for Customers using the Facebook Api
    """
    adapter_class = FacebookOAuth2Adapter


class ConvertToken(generics.GenericAPIView):
    """
    Converts Facebook token to Oauth2 Token
    """
    serializer_class = serializers.ConvertTokenSerializer

    def post(self, request):
        message = {}
        serializer = serializers.ConvertTokenSerializer(data=request.data)
        if serializer.is_valid():
            application = Application.objects.all()[0]
            token = Auth_Token.objects.get(key=serializer.data['key'])
            expires = datetime.now() + timedelta(days=180)
            access_token = AccessToken(
                user=token.user,
                scope='read write groups',
                expires=expires,
                token=common.generate_token(),
                application=application
            )
            access_token.save()
            customer_count = Customer.objects.filter(user=token.user).count()
            if customer_count == 0:
                customer = Customer()
                customer.user = token.user
                customer.save()
            message['access_token'] = access_token.token
            message['expires_in'] = 3600
            message['token_type'] = "Bearer"
            message['scope'] = access_token.scope
            message['refresh_token'] = access_token.token

            return Response(message, status.HTTP_200_OK)
        else:
            message['status'] = 'error'
            return Response(message, status.HTTP_401_UNAUTHORIZED)


class CategoryList(BestPraticsList, generics.ListAPIView):
    """
    Lists the available Categories in the customer App
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    search_fields = ('name',)
    filter_fields = ('name',)
    ordering = 'ordering'

    def get_queryset(self):
        queryset = super(CategoryList, self).get_queryset()
        queryset = queryset.filter()
        query_params = self.request.query_params
        gender = query_params.get('gender', None)
        if not self.request.user.is_superuser:
            queryset = queryset.filter(is_demo=False)
        if gender:
            if gender == 'male':
                queryset = queryset.filter(gender__in=['Todos', 'Masculino'])
            if gender == 'female':
                queryset = queryset.filter(gender__in=['Todos', 'Feminino'])
        return queryset


class ServiceList(BestPraticsList, generics.ListAPIView):
    """
    Lists the available Services for a chosen Category in the customer App
    """
    queryset = Service.objects.all()
    serializer_class = serializers.ServiceSerializer
    search_fields = ('name',)
    ordering = 'name'
    filter_fields = ('name', 'category',)

    def get_queryset(self):
        queryset = super(ServiceList, self).get_queryset().select_related('category')\
            .filter(is_app_enabled=True)
        queryset = queryset.filter()
        query_params = self.request.query_params
        gender = query_params.get('gender', None)
        if gender:
            if gender == 'male':
                queryset = queryset.filter(gender__in=['Todos', 'Masculino'])
            if gender == 'female':
                queryset = queryset.filter(gender__in=['Todos', 'Feminino'])
        return queryset


class AttendanceList(BestPraticsList, generics.ListCreateAPIView):
    """
    Lists the Attendances for the current Customer or Professional in either App, filtering by their Status
    """
    queryset = Attendance.objects.select_related(
                                             'customer__user', 'professional__user','initial_service__category',
                                             'credit_card','customer__user','address',
                                             'pricing_criterion_option__pricing_criterion')\
                                             .prefetch_related('attendance_relation__service__category')
    serializer_class = serializers.AttendanceSerializer
    search_fields = ('id',)
    ordering = 'id'
    filter_fields = ('status',)
    # permission_classes = [TokenHasReadWriteScope]

    def get_queryset(self):
        if self.request.user.is_anonymous():
            return self.queryset.none()
        else:
            query = self.queryset.exclude(status__in=['draft','flexible_draft', 'completed_draft'])
            query_params = self.request.query_params
            historic = query_params.get('historic', None)
            status = query_params.get('status', None)
            get_type = query_params.get('get_type', None)
            flexible = query_params.get('flexible', "0")
            professional_parameter = query_params.get('professional', None)
            ordering = 'scheduling_date'
            query = self.queryset.exclude(status__in=['draft', 'flexible_draft'])
            if flexible == "0":
                query = query.filter(scheduling_date__isnull=False)\
                              .exclude(status__in=['complete_draft'])
            if historic is not None:
                if historic == 'true':
                    ordering = '-scheduling_date'
                    query = query.filter(
                        Q(status__in=['completed', 'canceled_by_customer', 'canceled_by_professional', 'expired',
                                      'pending_payment','scheduling_shock', 'rejected']) | Q(scheduling_date__lte=datetime.now()))
                else:
                    ordering = 'scheduling_date'
                    query = query.exclude(
                        Q(status__in=['completed', 'canceled_by_customer', 'canceled_by_professional', 'expired',
                                      'pending_payment', 'scheduling_shock', 'rejected']) | Q(scheduling_date__lte=datetime.now() - timedelta(hours=2)))
            user = self.request.user
            customer = Customer.objects.filter(user=user)
            professional = Professional.objects.filter(user=user)
            if customer.exists() and flexible == "0":
                return query.filter(customer__user=user).order_by(ordering)
            elif customer.exists() and flexible == "1" and status == "waiting_confirmation":
                return query.filter(customer__user=user, flexible_date_start__isnull=False, status="waiting_confirmation").order_by(ordering)
            if professional.exists():
                #if user is professional, override query
                if status is not None:
                    if flexible == "0" and status == 'waiting_confirmation':
                        #filters query for the given user as the professional, status = waiting confirmation
                        waiting_confirmation_query = list(AttendanceProfessionalConfirmation.objects
                                                          .filter(professional__user=user, is_closed=False)
                                                          .values_list('attendance__pk', flat=True))
                        #re validates status as waiting confirmation, add filter for scheduling_date
                        query = Attendance.objects.filter(scheduling_date__isnull=False, status='waiting_confirmation',
                                                          scheduling_date__gte=datetime.now()).select_related(
                            'customer__user', 'professional__user','initial_service__category', 'credit_card',
                            'customer__user','address','pricing_criterion_option__pricing_criterion')\
                            .prefetch_related('attendance_relation__service__category')
                        #query filtered by waiting confirmation status or profession__user= the given user
                        query = query.filter(Q(pk__in=waiting_confirmation_query)|Q(professional__user=user))\
                            .order_by(ordering)
                    elif flexible == "1" and status == 'waiting_confirmation':
                        #filters query for the given user as the professional, status = waiting confirmation
                        waiting_confirmation_query = list(AttendanceProfessionalConfirmation.objects
                                                          .filter(professional__user=user, is_closed=False)
                                                          .values_list('attendance__pk', flat=True))
                        #re validates status as waiting confirmation, add filter for scheduling_date, adds flexible_date_start__isnull
                        query = Attendance.objects.filter(scheduling_date__isnull=False, flexible_date_start__isnull=False, status='waiting_confirmation',
                                                          scheduling_date__gte=datetime.now()).select_related(
                            'customer__user', 'professional__user','initial_service__category', 'credit_card',
                            'customer__user','address','pricing_criterion_option__pricing_criterion')\
                            .prefetch_related('attendance_relation__service__category')
                        #query filtered by waiting confirmation status or profession__user= the given user, same as prev but adds flex_start
                        query = query.filter(Q(pk__in=waiting_confirmation_query)|Q(professional__user=user))\
                            .order_by(ordering)
                    elif flexible == "1" and status == 'complete_draft':
                        query = Attendance.objects.filter(flexible_date_start__isnull=False, status='complete_draft',
                                                          ).select_related(
                            'customer__user', 'professional__user','initial_service__category', 'credit_card',
                            'customer__user','address','pricing_criterion_option__pricing_criterion')\
                            .prefetch_related('attendance_relation__service__category')
                        query = query.order_by(ordering)
                    else:
                        query = query.filter(professional__user=user).order_by(ordering)
                else:
                    if get_type == "available":
                        # Scheduled attendances
                        waiting_confirmation_query = list(AttendanceProfessionalConfirmation.objects
                                                          .filter(professional__user=user, is_closed=False)
                                                          .values_list('attendance__pk', flat=True))
                        query1 = Attendance.objects.filter(scheduling_date__isnull=False,
                                                          scheduling_date__lte=datetime.now()).select_related(
                            'customer__user', 'professional__user','initial_service__category', 'credit_card',
                            'customer__user','address','pricing_criterion_option__pricing_criterion')\
                            .prefetch_related('attendance_relation__service__category')
                        query1 = query1.filter(Q(pk__in=waiting_confirmation_query)|Q(professional__user=user))\
                            .order_by(ordering)

                        # Flexible attendances
                        query2 = Attendance.objects.filter(flexible_date_start__isnull=False, status='complete_draft',
                                                          ).select_related(
                            'customer__user', 'professional__user','initial_service__category', 'credit_card',
                            'customer__user','address','pricing_criterion_option__pricing_criterion')\
                            .prefetch_related('attendance_relation__service__category')
                        query2 = query2.order_by(ordering)

                        query = query1 | query2
                    else:
                        query = query.filter(professional__user=user).exclude(status='waiting_confirmation').order_by(ordering)
                return query

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.AttendanceCreateSerializer
        else:
            return self.serializer_class

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, partial=True) # FIXME permitindo patch
        if serializer.is_valid():
            model = Attendance()
            if 'pixel_id' in serializer.data:
                model.pixel_id = serializer.data.get('pixel_id', None)
            service = serializer.data.get('service', None)
            professional = serializer.data.get('professional', None)
            if request.user.is_anonymous():
                if service is not None:
                    initial_service = Service.objects.get(pk=serializer.data['service'])
                    model.initial_service = initial_service
                    model.save()
            else:
                customer = Customer.objects.get(user=request.user)
                model.customer = customer
                credit_cards = Card.objects.filter(customer=customer).order_by('-created')
                address = UserAddress.objects.filter(user=request.user).order_by('-created')
                if credit_cards.exists():
                    model.credit_card = credit_cards[0]
                if address.exists():
                    model.address = address[0]
                if professional is not None:
                    model.professional = Professional.objects.get(pk=professional)
                if service is not None:
                    initial_service = Service.objects.get(pk=serializer.data['service'])
                    pricing_criterion = initial_service.pricing_criterion
                    if pricing_criterion:
                        option_customer = PricingCriterionCustomer.objects.filter(customer=customer, pricing_criterion=pricing_criterion)
                        if option_customer.exists():
                            model.pricing_criterion_option = option_customer[0].pricing_criterion_option
                        else:

                            if not initial_service.has_pricing_before:
                                if initial_service.default_option:
                                    model.pricing_criterion_option = initial_service.default_option
                    model.initial_service = initial_service
                    model.save()
                else:
                    services = serializer.data['services']
                    model.initial_service = Service.objects.get(pk=ServiceProfessional.objects.get(pk=services[0]['id']).service_id)
                    model.save()
                    for item in services:
                        professional_service = ServiceProfessional.objects.get(pk=item['id'])
                        attendanceservice = AttendanceService(attendance=model, service=professional_service.service)
                        attendanceservice.price = professional_service.minimum_price
                        attendanceservice.duration = professional_service.average_time
                        attendanceservice.save()
                pixel_feedback.delay(model.pk, 'AddToCart')
            serializer = serializers.AttendanceSerializer(model, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Gets the detailed information for a chosen Attendance
    """

    # permission_classes = [TokenHasReadWriteScope]
    queryset = Attendance.objects.select_related(
        'customer__user', 'professional__user','initial_service__category', 'credit_card','customer__user','address',
        'pricing_criterion_option__pricing_criterion').prefetch_related('attendance_relation__service__category')
    serializer_class = serializers.AttendanceSerializer

    def get_queryset(self):
        if self.request.user.is_anonymous():
            return self.queryset
        else:
            user = self.request.user
            customer = Customer.objects.filter(user=user)
            professional = Professional.objects.filter(user=user)
            if customer.exists():
                return self.queryset.filter(customer__user=user)
            if professional.exists():
                waiting_confirmation_query = list(
                    AttendanceProfessionalConfirmation.objects.filter(professional__user=user, is_closed=False).values_list(
                        'attendance__pk', flat=True))
                return self.queryset.filter(Q(pk__in=waiting_confirmation_query)|Q(professional__user=user))


class UpdateFlexAttendance(APIView):
    #this endpoint is used to update the flexible attendance dates / hours
    #then calculate the factor based on the dates / hours
    #and update the total_price of the attendance as well as other values by running save()

    def patch(self, request, *args, **kwargs):
        attendance = Attendance.objects.get(pk=kwargs['pk'])
        flexible_date_start = parser.isoparse(request.data['flexible_date_start'])
        flexible_date_end = parser.isoparse(request.data['flexible_date_end'])
        if request.data['status'] == 'flexible_draft':
            if attendance.flexible_date_start != flexible_date_start or attendance.flexible_date_end != flexible_date_end:
                attendance.update_factor(
                    flexible_date_start = flexible_date_start,
                    flexible_date_end = flexible_date_end)
        try:
            instance = Attendance.objects.get(pk=kwargs['pk'])
            serializer = serializers.AttendanceUpdateSerializer(instance=instance,data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data,status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Attendance.DoesNotExist:
            serializer = serializers.AttendanceUpdateSerializer(data=request.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceUpdateAnonymous(generics.GenericAPIView):
    """
    Updates current Attendance for Anonymous user in the Customer App
    """
    # permission_classes = [TokenHasReadWriteScope]
    queryset = Attendance.objects.select_related(
        'customer__user', 'professional__user','initial_service__category', 'credit_card','customer__user','address',
        'pricing_criterion_option__pricing_criterion').prefetch_related('attendance_relation__service__category')
    serializer_class = serializers.AttendanceSerializer

    def post(self, request, *args, **kwargs):
        attendance = Attendance.objects.select_related(
            'customer__user', 'professional__user', 'initial_service__category', 'credit_card', 'customer__user',
            'address',
            'pricing_criterion_option__pricing_criterion', 'neighborhood__city').get(pk=kwargs['pk'])
        if not attendance.customer:
            customer = Customer.objects.filter(user=request.user)
            if customer.exists():
                customer = customer[0]
                attendance.customer = customer
                attendance.save()
                serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response({}, status=status.HTTP_400_BAD_REQUEST)

class AttendanceProfessional(generics.ListCreateAPIView):
    """
    Lists the available Professionals for an Attendance based on chosen Service, Location and Schedule
    """
    # permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.ProfessionalSerializerListAttentance

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.AttendanceProfessionalSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        attendance = Attendance.objects.select_related(
        'customer__user', 'professional__user','initial_service__category', 'credit_card','customer__user','address',
        'pricing_criterion_option__pricing_criterion', 'neighborhood__city').get(pk=self.kwargs['pk'])
        query_params = self.request.query_params
        scheduling = query_params.get('scheduling', None)
        service_time = timedelta(minutes=attendance.initial_service.mean_range_time + 60)
        if attendance.neighborhood:
            city = attendance.neighborhood.city.name
            neighborhood = attendance.neighborhood.description
        else:
            neighborhood = attendance.address.neighborhood
            city = attendance.address.city.upper()
        neighborhood_model = Neighborhood.objects.filter(city__name=city,description__iexact=neighborhood)
        if neighborhood_model.exists():
            neighborhood_model = neighborhood_model[0]
            if neighborhood_model.father:
                neighborhood = neighborhood_model.father.description
        if attendance.services:
            service_time = timedelta(minutes=attendance.total_duration + 60)
        data_atual = datetime.now()
        professional = Professional.objects.filter(professional_enabled=True,professional_enabled_executive=True)\
            .select_related('user').filter(services__service=attendance.initial_service, services__is_removed=False,
                    citys__city__name=city,citys__neighborhoods__description=neighborhood)
        if scheduling is None:
            professional = professional.filter(
                Q(Q(schedules__daily_date__gt=data_atual.date()) & Q(Q(schedules__attendance__isnull=True)|Q(is_saloon=True)),
                  schedules__daily_time_begin__lte=F('schedules__daily_time_end') - service_time) |
                Q(Q(schedules__attendance__isnull=True)|Q(is_saloon=True), schedules__daily_date=data_atual.date(),
                  schedules__daily_time_begin__lte=data_atual.time(),
                  schedules__daily_time_end__gte=(data_atual + service_time).time()),
                Q(schedules__is_removed=False)|Q(is_saloon=True)).distinct()
        if scheduling == "true":
            professional = professional.filter(Q(Q(schedules__attendance__isnull=True)|Q(is_saloon=True))&
                                               Q(Q(schedules__is_removed=False)|Q(is_saloon=True))&
                                               Q(schedules__daily_date=attendance.scheduling_date.date(),
                                               schedules__daily_time_begin__lte=attendance.scheduling_date.time(),
                                               schedules__daily_time_end__gte=(attendance.scheduling_date + service_time).time())).distinct()
            """ professional = professional.exclude(Q(remove_schedules__service_professional__service=attendance.initial_service)&
                                               Q(remove_schedules__daily_date=attendance.scheduling_date.date(),
                                               remove_schedules__daily_time_begin__lte=attendance.scheduling_date.time(),
                                               remove_schedules__daily_time_end__gte=(attendance.scheduling_date + service_time).time())).distinct() """
        if scheduling == "semi_flexible":
            professional = professional.filter(
                                            Q(Q(schedules__daily_time_begin__lte=F('schedules__daily_time_end') - service_time)) &
                                               Q(schedules__daily_time_begin__lte=attendance.flexible_date_end.time()),
                                               # schedules__daily_time_begin__lte=F('schedules__daily_time_end') - service_time,
                                               # schedules__daily_time_begin__lte=attendance.flexible_date_end.time(),
                                               Q(schedules__daily_time_end__gte=(attendance.flexible_date_start + service_time).time())
                                               & Q(schedules__attendance__isnull=True)|Q(is_saloon=True)
                                               & Q(schedules__is_removed=False)|Q(is_saloon=True),
                                               schedules__daily_date=attendance.flexible_date_start.date()).distinct()
            """ professional = professional.exclude(
                                            Q(Q(remove_schedules__daily_time_begin__lte=F('schedules__daily_time_end') - service_time)) &
                                               Q(remove_schedules__service_professional__service=attendance.initial_service)&
                                               Q(remove_schedules__daily_time_end__lte=attendance.flexible_date_end.time()),
                                               Q(remove_schedules__daily_time_end__gte=(attendance.flexible_date_start + service_time).time()),
                                               remove_schedules__daily_date=attendance.flexible_date_start.date()).distinct() """


        if attendance.pricing_criterion_option:
            professional = professional.filter(
                services__service_professional__pricingcriterionoptions=attendance.pricing_criterion_option,
                services__service_professional__pricingcriterionoptions__is_removed=False
            ).distinct()
        gender = query_params.get('gender', None)
        if gender is not None:
            professional = professional.filter(Q(gender_attendance='all') | Q(gender_attendance=gender))
        professional = professional.filter(services__service=attendance.initial_service, services__enabled=True )
        return professional

    def get_serializer_context(self):
        attendance = Attendance.objects.select_related(
        'customer', 'initial_service', 'customer__user', 'pricing_criterion_option').get(pk=self.kwargs['pk'])
        professional_favorites = Professional.objects.none()
        if not self.request.user.is_anonymous():
            professional_favorites = Professional.objects.filter(customer_favorites__customer=attendance.customer,
                                                             customer_favorites__is_removed=False).values_list('pk', flat=True)
        return {'request': self.request, 'service': attendance.initial_service,
                'pricing_criterion_option': attendance.pricing_criterion_option,
                'professional_favorites': professional_favorites}

    def get(self, request, *args, **kwargs):
        if not self.request.user.is_anonymous():
            customer = Customer.objects.get(user=request.user)
        attendance = Attendance.objects.get(pk=self.kwargs['pk'])
        professionals = self.get_queryset()
        professionals_visualizations = []
        for professional in professionals:
            if self.request.user.is_anonymous():
                professionals_visualizations.append(ProfessionalVisualisation(professional_id=professional.pk, attendance_id=attendance.pk, type='list', position=1 + list(professionals).index(professional)))
            else:
                professionals_visualizations.append(ProfessionalVisualisation(customer_id=customer.pk, professional_id=professional.pk, attendance_id=attendance.pk, type='list', position=1 + list(professionals).index(professional)))
        ProfessionalVisualisation.objects.bulk_create(professionals_visualizations)
        pixel_feedback.delay(attendance.pk, 'ViewContent')
        return super().get(self, request, *args, **kwargs)

    def get_paginated_response(self, data):
        #This s.data['price] is the value for dont have preference
        s = super().get_paginated_response(data)
        attendance = Attendance.objects.get(pk=self.kwargs['pk'])
        s.data['price'] = None
        if attendance.address:
            #professional_for_price = Professional.objects.filter(address__city__iexact=attendance.address.city)
            service_professional = attendance.get_biuri_click_price()
            if service_professional.exists():
                service_professional = service_professional[0]
                if attendance.pricing_criterion_option:
                    service_professional_criterion = ServiceProfessionalPricingCriterion.objects.filter(
                        service_professional=service_professional, pricingcriterionoptions=attendance.pricing_criterion_option)
                    if service_professional_criterion.exists():
                        service_professional_criterion = service_professional_criterion.first()
                        s.data['price'] = service_professional_criterion.price
                    else:
                        s.data['price'] = service_professional.minimum_price
                else:
                    s.data['price'] = service_professional.minimum_price
        return s

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            attendance = Attendance.objects.get(pk=kwargs['pk'])
            professional_id = serializer.data['professional']
            if professional_id != 0:
                attendance.professional = Professional.objects.get(pk=serializer.data['professional'])
                attendance.type = 'has_preference'
                attendance.factor = 1.00
                super(Attendance, attendance).save()
            else:
                attendance.type = 'dont_has_preference'
                attendance.professional = None
            attendance.save()
            serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            attendance = Attendance.objects.get(pk=kwargs['pk'])
            professional_id = 0
            attendance.type = 'dont_has_preference'
            attendance.professional = None
            attendance.save()
            serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceAddress(generics.GenericAPIView):
    """
    Attaches a chosen Address or Neighborhood to the current Attendance during it's creation in the App
    """
    serializer_class = serializers.AttendanceAddressSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            attendance = Attendance.objects.get(pk=kwargs['pk'])
            if 'address' in serializer.data:
                attendance.address = UserAddress.objects.get(pk=serializer.data['address'])
            if 'neighborhood' in serializer.data:
                attendance.neighborhood = Neighborhood.objects.get(pk=serializer.data['neighborhood'])
            attendance.save()
            serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceCreditCard(generics.GenericAPIView):
    """
    Attaches the chosen Credit Card to the Current Attendance in the App
    """
    serializer_class = serializers.AttendanceCreditCardSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            attendance = Attendance.objects.select_related(
        'customer__user', 'professional__user','initial_service__category', 'credit_card','customer__user','address',
        'pricing_criterion_option__pricing_criterion').get(pk=kwargs['pk'])
            attendance.credit_card = Card.objects.get(pk=serializer.data['credit_card'])
            attendance.save()
            serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceProfessionalAccepted(generics.GenericAPIView):
    """
    Allows a Professional to accept an Attendance or rejects their acceptance if the Attendance has an active Professional attached to it
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.AttendanceAcceptedPostSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            attendance = Attendance.objects.select_related(
        'customer__user', 'professional__user','initial_service__category', 'credit_card','customer__user','address',
        'pricing_criterion_option__pricing_criterion').get(pk=kwargs['pk'])
            professional = Professional.objects.get(user=request.user)
            if professional == attendance.professional:
                attendance.status = 'confirmated'
                attendance.save()
            else:
                if not attendance.professional:
                    AttendanceProfessionalConfirmation.objects.filter(attendance=attendance).update(is_closed=True)
                    attendance.professional = professional
                    attendance.save()
                    attendance.status = 'confirmated'
                    attendance.save()
                elif attendance.status == 'confirmated':
                    return Response({'error': 'Este atendimento já foi confirmado por outro Profissional.'},
                                    status=status.HTTP_400_BAD_REQUEST)
            serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendancePricingCriterionOptions(generics.ListCreateAPIView):
    """
    Allows the Customer to choose the Pricing Criterion Option for the current Attendance
    """
    # permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.AttentancePricingCriterionSerializer
    queryset = PricingCriterion.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.AttendancePricingCriterionOptionsSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        attendance = Attendance.objects.select_related('initial_service__pricing_criterion').get(pk=self.kwargs['pk'])
        if attendance.initial_service.pricing_criterion:
            pricingcriterion = PricingCriterion.objects.get(pk=attendance.initial_service.pricing_criterion.pk)
        else:
            pricingcriterion = PricingCriterion.objects.none()
        return pricingcriterion

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            attendance = Attendance.objects.select_related(
        'customer__user', 'professional__user','initial_service__category', 'credit_card','customer__user','address',
        'pricing_criterion_option__pricing_criterion').get(pk=kwargs['pk'])
            attendance.observation = serializer.data['observation']
            if (serializer.data.get('pricing_criterion_option', None)):
                pricing_criterion_option = PricingCriterionOptions.objects.get(
                    pk=serializer.data['pricing_criterion_option'])
                attendance.pricing_criterion_option = pricing_criterion_option
                if not self.request.user.is_anonymous():
                    pricing_criterion_customer = PricingCriterionCustomer.objects.filter(pricing_criterion=pricing_criterion_option.pricing_criterion, customer=attendance.customer)
                    if pricing_criterion_customer.exists():
                        pricing_criterion_customer = pricing_criterion_customer[0]
                    else:
                        pricing_criterion_customer = PricingCriterionCustomer(customer=attendance.customer,pricing_criterion=pricing_criterion_option.pricing_criterion)
                    pricing_criterion_customer.pricing_criterion_option = pricing_criterion_option
                    pricing_criterion_customer.save()
            attendance.save()
            serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        if self.get_queryset():
            serializer = self.get_serializer(self.get_queryset(), context={'request': request}).data
        else:
            serializer = {}
        return Response(serializer, status=status.HTTP_200_OK)


class AttendanceSchedule(generics.GenericAPIView):
    """
    Lists the available Schedule Times for the chosen Professional in the Customer App
    """
    # permission_classes = [TokenHasReadWriteScope]
    queryset = Attendance.objects.all()

    def roundTime(self, dt=None):
        """Round a datetime object to any time lapse in seconds
        dt : datetime.datetime object, default now.
        roundTo : Closest number of seconds to round to, default 1 minute.
        Author: Thierry Husson 2012 - Use it as you want but don't blame me.
        """
        dt = dt.replace(second=0)
        if dt.minute == 0:
            return dt
        if dt.minute < 30:
            return dt.replace(minute=30)
        return dt.replace(minute=0) + timedelta(hours=1)

    def get(self, request, *args, **kwargs):
        attendance = Attendance.objects.get(pk=kwargs['pk'])
        schedules = []
        datetime_agora = datetime.now()
        if attendance.total_duration > 0:
            duration = attendance.total_duration
        else:
            duration = attendance.initial_service.mean_range_time
            if attendance.professional:
                service = ServiceProfessional.objects.filter(service=attendance.initial_service,
                                                             professional=attendance.professional)
                if service.exists():
                    service = service.first()
                    duration = service.average_time
        if attendance.professional:
            dates = []
            if attendance.professional.is_saloon:
                professional_sheddules = Schedule.objects.filter(professional=attendance.professional).filter(
                    (Q(daily_date__gt=datetime_agora.date()) | Q(daily_date=datetime_agora.date(),
                                                                daily_time_begin__lte=datetime_agora.time()))).order_by(
                    'daily_date', 'daily_time_begin').distinct()
                #add logic
            else:

                professional_sheddules = Schedule.objects.filter(attendance__isnull=True,
                                                                professional=attendance.professional).filter(
                    (Q(daily_date__gt=datetime_agora.date()) | Q(daily_date=datetime_agora.date(),
                                                                daily_time_begin__lte=datetime_agora.time()))).order_by(
                    'daily_date', 'daily_time_begin').distinct()
            for professional_sheddule in professional_sheddules:
                date = datetime.combine(professional_sheddule.daily_date, professional_sheddule.daily_time_begin)
                if date < datetime.now():
                    date = self.roundTime(datetime.now() + timedelta(hours=8))
                if date.date() == (datetime.now() + timedelta(days=1)).date():
                    now = datetime.now()
                    interval_increment = now.replace(hour=21, minute=0) - now
                    if interval_increment > timedelta(minutes=1):
                        date_new = self.roundTime(date.replace(hour=8, minute=0) + timedelta(hours=8) - interval_increment)
                        if date_new > date:
                            date = date_new
                    else:
                        date_new = self.roundTime(date.replace(hour=8, minute=0) + timedelta(hours=8))
                        if date_new > date:
                            date = date_new
                date_final = datetime.combine(professional_sheddule.daily_date, professional_sheddule.daily_time_end)
                counter = int(int((date_final - date).total_seconds() / 60) / duration) + 1
                if counter >= 1:
                    hours = list(
                        rrule.rrule(rrule.MINUTELY, interval=duration, count=counter,
                                    dtstart=date))
                    hours_list = []
                    for hour, next_hour in zip(hours, hours[1:] + [hours[0]]):
                        hours_list.append({'hour_initial': hour, 'hour_final': next_hour})
                    hours_list = hours_list[:-1]
                    if date.date() in dates:
                        for i in schedules:
                            if i['date'] == date.date():
                                schedules[len(dates) - 1]['hours'] = schedules[len(dates) - 1]['hours'] + hours_list
                    else:
                        dates.append(date.date())
                        schedules.append({'date': date.date(), 'hours': hours_list})

        else:
            datas = list(rrule.rrule(rrule.DAILY, count=15, dtstart=datetime.now().date()))
            for date in datas:
                if date.date() == datetime.now().date() :
                    date = self.roundTime(datetime.now() + timedelta(hours=8))
                    if date < (date.replace(hour=8, minute=0) + timedelta(hours=8)):
                        date = date.replace(hour=8, minute=0) + timedelta(hours=8)
                else:
                    if date.date() == (datetime.now() + timedelta(days=1)).date():
                        now = datetime.now()
                        interval_increment = now.replace(hour=21, minute=0) - now
                        if interval_increment > timedelta(minutes=1) and interval_increment < timedelta(hours=8):
                            date = self.roundTime(date.replace(hour=8, minute=0) + timedelta(hours=8) - interval_increment)
                        else:
                            date = self.roundTime(date.replace(hour=8, minute=0))
                    else:
                        date = date.replace(hour=8, minute=0)
                date_final = date.replace(hour=21, minute=00)
                counter = int(
                    int((date_final - date).total_seconds() / 60) / duration) + 1
                if counter > 1:
                    hours = list(rrule.rrule(rrule.MINUTELY, interval=duration
                                             , count=counter, dtstart=date))
                    hours_list = []
                    for hour, next_hour in zip(hours, hours[1:] + [hours[0]]):
                        hours_list.append({'hour_initial': hour, 'hour_final': next_hour})
                    hours_list = hours_list[:-1]
                    schedules.append({'date': date.date(), 'hours': hours_list})
        if len(schedules) < 1:
            return Response('Não há horários disponíveis.')
        else:
            #removing available times before 7am or after 8pm
            for day in schedules:
                aux = day["hours"].copy()
                for hour in day["hours"]:
                    if hour["hour_initial"].hour < 7 or hour["hour_final"].hour > 20 or (hour["hour_final"].hour >= 20 and hour["hour_final"].minute > 0):
                        aux.remove(hour)
                day["hours"] = aux
        # remove schedules for busy saloons with disabled services
        print('schedules[0]')
        print(schedules[0]['date'])
        for blocked_service in SaloonScheduleRemove.objects.filter(
            service_professional__service=attendance.initial_service,
            professional=attendance.professional
        ):
            print('found something')
            # print(schedules)
            for day in schedules:
                if day['date'] == blocked_service.daily_date:
                    print('day: ', day['date'])
                    print('blocked service: ', blocked_service)
                    aux = day["hours"].copy()
                    for hour in day["hours"]:
                        if int(blocked_service.daily_time_begin.hour) < int(hour["hour_initial"].hour) < int(blocked_service.daily_time_end.hour) or int(blocked_service.daily_time_begin.hour) < int(hour["hour_final"].hour) < int(blocked_service.daily_time_end.hour):
                            aux.remove(hour)

                        if int(blocked_service.daily_time_begin.hour) == int(hour["hour_initial"].hour):
                            if int(blocked_service.daily_time_begin.minute) <= int(hour["hour_initial"].minute):
                                if int(blocked_service.daily_time_end.hour) > int(hour["hour_initial"].hour):
                                    try:
                                        aux.remove(hour)
                                    except:
                                        pass
                                if int(blocked_service.daily_time_end.hour) == int(hour["hour_initial"].hour):
                                    if int(blocked_service.daily_time_end.minute) >= int(hour["hour_initial"].minute):
                                        try:
                                            aux.remove(hour)
                                        except:
                                            pass
                        if int(blocked_service.daily_time_end.hour) == int(hour["hour_initial"].hour):
                            if int(blocked_service.daily_time_end.minute) >= int(hour["hour_initial"].minute):
                                if int(blocked_service.daily_time_begin.hour) < int(hour["hour_initial"].hour):
                                    try:
                                        aux.remove(hour)
                                    except:
                                        pass
                                if int(blocked_service.daily_time_begin.hour) == int(hour["hour_initial"].hour):
                                    if int(blocked_service.daily_time_begin.minute) <= int(hour["hour_initial"].minute):
                                        try:
                                            aux.remove(hour)
                                        except:
                                            pass
                        if int(blocked_service.daily_time_begin.hour) == int(hour["hour_final"].hour):
                            if int(blocked_service.daily_time_begin.minute) <= int(hour["hour_final"].minute):
                                if int(blocked_service.daily_time_end.hour) > int(hour["hour_final"].hour):
                                    try:
                                        aux.remove(hour)
                                    except:
                                        pass
                                if int(blocked_service.daily_time_end.hour) == int(hour["hour_final"].hour):
                                    if int(blocked_service.daily_time_end.minute) >= int(hour["hour_final"].minute):
                                        try:
                                            aux.remove(hour)
                                        except:
                                            pass
                        if int(blocked_service.daily_time_end.hour) == int(hour["hour_final"].hour):
                            if int(blocked_service.daily_time_end.minute) >= int(hour["hour_final"].minute):
                                if int(blocked_service.daily_time_begin.hour) < int(hour["hour_final"].hour):
                                    try:
                                        aux.remove(hour)
                                    except:
                                        pass
                                if int(blocked_service.daily_time_begin.hour) == int(hour["hour_final"].hour):
                                    if int(blocked_service.daily_time_begin.minute) <= int(hour["hour_final"].minute):
                                        try:
                                            aux.remove(hour)
                                        except:
                                            pass
                        if int(blocked_service.daily_time_begin.hour) == int(hour["hour_initial"].hour) and int(blocked_service.daily_time_end.hour) == int(hour["hour_final"].hour):
                            if int(blocked_service.daily_time_begin.minute) <= int(hour["hour_initial"].minute):
                                try:
                                    aux.remove(hour)
                                except:
                                    pass
                            if int(blocked_service.daily_time_begin.minute) <= int(hour["hour_final"].minute):
                                try:
                                    aux.remove(hour)
                                except:
                                    pass
                            if int(blocked_service.daily_time_end.minute) >= int(hour["hour_initial"].minute):
                                try:
                                    aux.remove(hour)
                                except:
                                    pass
                            if int(blocked_service.daily_time_end.minute) >= int(hour["hour_final"].minute):
                                try:
                                    aux.remove(hour)
                                except:
                                    pass
                            #block occurs inside the interval:
                            if int(blocked_service.daily_time_begin.minute) >= int(hour["hour_initial"].minute) and int(blocked_service.daily_time_end.minute) <= int(hour["hour_final"].minute):
                                try:
                                    aux.remove(hour)
                                except:
                                    pass
                    day["hours"] = aux
        return Response(schedules, status=status.HTTP_200_OK)


class ProfessionalDetail(generics.RetrieveAPIView):
    """
    Returns the Detailed Information for the chosen Professional in the Customer App
    """
    queryset = Professional.objects.select_related('user').prefetch_related('badges', 'evaluations')
    serializer_class = serializers.ProfessionalDetailSerializer

    def get(self, request, *args, **kwargs):
        if self.request.user.is_anonymous():
            ProfessionalVisualisation.objects.create(professional=self.get_object(), type='profile')
        else:
            customer = Customer.objects.get(user=request.user)
            ProfessionalVisualisation.objects.create(customer=customer, professional=self.get_object(), type='profile')
        return super().get(self, request, *args, **kwargs)


class ProfessionalListApi(generics.ListAPIView):
    """
    Lists the available Professionals in the Customer App
    """
    queryset = Professional.objects.filter(professional_enabled=True, professional_enabled_executive=True).select_related('user', 'category').prefetch_related('badges', 'evaluations')
    serializer_class = serializers.ProfessionalDetailSerializer

    def get_queryset(self):
        query = self.queryset
        query_params = self.request.query_params
        q = query_params.get('q', None)
        if q is not None:
            q = q.strip().lower()
            q = unidecode.unidecode(q)
            query = query.filter(search_text__icontains=q)
        gender = query_params.get('gender', None)
        if gender is not None:
            query = query.filter(Q(gender_attendance='all')|Q(gender_attendance=gender))
        return query

    def get(self, request, *args, **kwargs):
        if not request.user.is_anonymous():
            customer = Customer.objects.get(user=request.user)
        professionals = self.get_queryset()
        professionals_visualisations = []
        for professional in professionals:
            if request.user.is_anonymous():
                professionals_visualisations.append(ProfessionalVisualisation(professional_id=professional.pk, type='search', position=1 + list(professionals).index(professional)))
            else:
                professionals_visualisations.append(ProfessionalVisualisation(customer=customer, professional_id=professional.pk, type='search', position=1 + list(professionals).index(professional)))
        ProfessionalVisualisation.objects.bulk_create(professionals_visualisations)
        return super().get(self, request, *args, **kwargs)


class RefreshToken(BestPraticsList, OAuthLibMixin, generics.GenericAPIView):
    """
    Refreshes the Authorization Token in either App
    """
    serializer_class = serializers.RefreshTokenSerializer
    server_class = oauth2_settings.OAUTH2_SERVER_CLASS
    validator_class = oauth2_settings.OAUTH2_VALIDATOR_CLASS
    oauthlib_backend_class = oauth2_settings.OAUTH2_BACKEND_CLASS

    def get(self, request, format=None):
        serializer = serializers.RefreshTokenSerializer()
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = serializers.RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            if hasattr(request.data, "_mutable"):
                request.data._mutable = True
            app = Application.objects.all()[0]
            request.data.update(
                {"grant_type": "refresh_token", "client_id": app.client_id, "client_secret": app.client_secret})
            url, headers, body, status = self.create_token_response(request)
            if status == 200:
                access_token = json.loads(body).get("access_token")
                if access_token is not None:
                    token = get_access_token_model().objects.get(
                        token=access_token)
                    app_authorized.send(
                        sender=self, request=request,
                        token=token)
            response = HttpResponse(content=body, status=status)
            for k, v in headers.items():
                response[k] = v
            return Response(json.loads(body), status=status.HTTP_200_OK)
        return Response(serializer.errors, status=400)


class CreditCard(BestPraticsList, generics.ListCreateAPIView):
    """
    Allows the Customer to list their Credit Cards and save a new one
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.CreditCardGetSerializer
    queryset = Card.objects.all()

    def get_queryset(self):
        customer = Customer.objects.filter(user=self.request.user)
        customer = customer[0] if customer else 0
        queryset = Card.objects.filter(customer=customer)
        return queryset

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.CreditCardPostSerializer
        else:
            return self.serializer_class

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        customer = Customer.objects.get(user=self.request.user)

        if serializer.is_valid():
            data = {
                'account_id': customer.iugu_client_id,
                'method': 'credit_card',
                'test': settings.DEBUG
                }
            first_name, last_name = serializer.data['name'].split(' ', 1)
            card = {
                'number': serializer.data['number'],
                'verification_value': serializer.data['verification_value'],
                'first_name': first_name,
                'last_name': last_name,
                'month': serializer.data['month'],
                'year': serializer.data['year']
            }
            data['data'] = card
            # month = card['month']
            # year = card['year']
            # today = date.today()
            # if (int(month) >= today.month and today.year == int(year)) or (int(year) > today.year):
            #     return Response(
            #         {'errors' : {
            #             'month': 'Validade Inválida'
            #             }
            #          }, status=400)
            token = Token().create(data)
            if 'errors' in token:
                return Response(token, status=400)
            card = Card(customer=customer, iugu_payment_token=token, card_data=data)
            card.save()
            serializer = serializers.CreditCardGetSerializer(card, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreditCardDetail(BestPraticsList, generics.RetrieveDestroyAPIView):
    """
    Returns the Details of a Chosen Credit Card
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.CreditCardGetSerializer
    queryset = Card.objects.all()

    def get_queryset(self):
        customer = Customer.objects.get(user=self.request.user)
        queryset = Card.objects.filter(pk=self.kwargs['pk'], customer=customer)
        return queryset


class Profile(generics.GenericAPIView):
    """
    Allows the User to see and update their Profile information in either App
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.ProfessionalSerializer
    queryset = User.objects.all()
    parser_class = (FileUploadParser,)

    def get_queryset(self):
        customer = Customer.objects.filter(user=self.request.user)
        if customer:
            return customer[0]
        else:
            professional = Professional.objects.get(user=self.request.user)
            return professional

    def get_serializer_class(self):
        customer = Customer.objects.filter(user=self.request.user)
        if self.request.method == "POST":
            return serializers.ProfileUpdateSerializer
        else:
            if customer:
                return serializers.CustomerSerializer
            else:
                return serializers.ProfessionalSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_queryset(), context={'request': request})
        return Response(serializer.data, status=200)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        avatar = request.data.get('avatar', None)
        if serializer.is_valid():
            user = self.request.user
            user.first_name = serializer.data['first_name']
            user.last_name = serializer.data['last_name']
            user.save()
            customer = Customer.objects.filter(user=user)
            professional = Professional.objects.filter(user=user)
            if customer:
                customer = customer[0]
                customer.birthday = serializer.data['birthday']
                customer.gender = serializer.data['gender']
                customer.celphone = serializer.data['celphone']
                if avatar is not None:
                    customer.avatar_image = request.data['avatar']
                customer.save()
            if professional:
                professional = professional[0]
                professional.birthday = serializer.data['birthday']
                professional.gender = serializer.data['gender']
                professional.celphone = serializer.data['celphone']
                if avatar is not None:
                    professional.avatar = request.data['avatar']
                professional.save()
            return Response({}, status=status.HTTP_200_OK)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppRegistrationAPI(generics.GenericAPIView):
    """
    Sends Push Token to the Api in either App
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.AppRegistration

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            token = PushToken.objects.filter(token=serializer.data['registration_id'])
            if token:
                push_token = token[0]
                push_token.user = self.request.user
                push_token.save()
            else:
                push_token = PushToken()
                push_token.token = serializer.data['registration_id']
                push_token.user = self.request.user
                push_token.save()
            return Response(response, status=status.HTTP_200_OK)
        return Response(response, status=status.HTTP_400_BAD_REQUEST)


class AddressAPI(APIView):
    """
    Returns the Address Information based on a given CEP
    """
    def get(self, request, cep):
        response = get_address(cep)
        return response


class ExistingEmailAPI(APIView):
    """
    Returns a Boolean value for an existing email
    """
    def get(self, request):
        query = User.objects.filter(email__iexact=request.GET['email'])
        if len(query)>0:
            response = {"exists": True}
            status_response = status.HTTP_400_BAD_REQUEST
        else:
            response = {"exists": False}
            status_response = status.HTTP_200_OK
        return Response(response, status=status_response)


class StateAPI(generics.ListAPIView):
    """
    Lists the States for the Customer App
    """
    queryset = State.objects.all()
    serializer_class = serializers.StateSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    ordering = 'description'
    filter_fields = '__all__'



class CityAPI(generics.ListAPIView):
    """
    Lists the Cities of a chosen State in the Customer App
    """
    queryset = City.objects.all()
    serializer_class = serializers.CitySerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    ordering = 'name'
    filter_fields = '__all__'


class NeighborhoodAPI(generics.ListAPIView):
    """
    Lists the Neighborhoods for a chosen City in the Customer App
    """
    queryset = Neighborhood.objects.filter(father__isnull=True)
    serializer_class = serializers.NeighborhoodSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,)
    ordering = 'description'
    filter_fields = '__all__'


class UserAddressApiList(generics.ListCreateAPIView):
    """
    Lists the registered Addresses for the current User in the Customer App
    """
    permission_classes = [TokenHasReadWriteScope]
    queryset = UserAddress.objects.all()
    serializer_class = serializers.UserAddressSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class UserAddressApiDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Details the chosen Address in the Customer App
    """
    permission_classes = [TokenHasReadWriteScope]
    queryset = UserAddress.objects.all()
    serializer_class = serializers.UserAddressSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class InitialStatus(generics.GenericAPIView):
    """
    Returns the Initial Navigation Status for either App based on Attendance Status
    """
    # permission_classes = [TokenHasReadWriteScope]

    def get(self, request):
        response = {}
        response['icon'] = ''
        response['title'] = ''
        response['text'] = ''
        response['screen'] = ''
        response['is_cancelable'] = False
        response['show_alert'] = False
        response['params'] = {}
        status = ['on_transfer', 'in_attendance']
        if not self.request.user.is_anonymous():
            professional = Professional.objects.filter(user=request.user)
            is_professional = False
            if professional.exists():
                is_professional = True
                attendance = Attendance.objects.filter(professional__user=request.user, status__in=status).order_by(
                    '-scheduling_date')
            else:
                attendance = Attendance.objects.filter(customer__user=request.user, status__in=status).order_by(
                    '-scheduling_date')
            response['news'] = []
            news = News.objects.all().order_by('-created')
            if news.exists():
                response['news'] = serializers.NewsSerializer(news[0], context={'request': request}).data
            if attendance.exists():
                attendance = attendance.first()
                response['params'] = serializers.AttendanceSerializer(attendance, context={'request': request}).data
                if attendance.status == 'on_transfer':
                    if is_professional:
                        response['title'] = 'Atendimento não finalizado'
                        response['text'] = 'Inicie o atendimento'
                        response['show_alert'] = False
                        response['screen'] = 'Details3'
                    else:
                        response['title'] = 'Atendimento não finalizado'
                        response['text'] = 'O profissional está a caminho do atendimento'
                        response['show_alert'] = False
                        response['screen'] = 'Comming'
                if attendance.status == 'in_attendance':
                    if is_professional:
                        response['title'] = 'Em atendimento'
                        response['text'] = 'Atendimento em aberto'
                        response['show_alert'] = False
                        response['screen'] = 'Details3'
                    else:
                        response['title'] = 'Em atendimento'
                        response['text'] = 'O profissional está em atendimento'
                        response['show_alert'] = False
                        response['screen'] = 'Comming'
            else:
                if is_professional:
                    attendance = Attendance.objects.filter(professional__user=request.user, status='completed',
                                                           has_evaluation=False).order_by('-scheduling_date')
                    if attendance.exists():
                        attendance = attendance.first()
                        response['title'] = 'Avaliacao Pendente'
                        response['text'] = 'Avaliacao Pendente'
                        response['show_alert'] = False
                        response['screen'] = 'Evaluation'
                        response['params'] = serializers.AttendanceSerializer(attendance, context={'request': request}).data
                else:
                    attendance = Attendance.objects.filter(customer__user=request.user, status='completed',
                                                           has_evaluation_professional=False).order_by('-scheduling_date')
                    if attendance.exists():
                        attendance = attendance.first()
                        response['title'] = 'Avaliacao Pendente'
                        response['text'] = 'Avaliacao Pendente'
                        response['show_alert'] = False
                        response['screen'] = 'Evaluation'
                        response['params'] = serializers.AttendanceSerializer(attendance, context={'request': request}).data
        return Response(response, status=200)


class ProfessionalEvaluationPostApi(generics.GenericAPIView):
    """
    Allows the Customer to post a Professional Evaluation related to the current Attendance
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.ProfessionalEvaluationPostSerializer

    def get(self, request, *args, **kwargs):
        response = {}
        evaluation_types = EvaluationType.objects.all()
        serializer = serializers.EvaluationTypeSerializer(evaluation_types, context={'request': request}, many=True)
        response['results'] = serializer.data
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            serializer = serializer.data
            attendance = Attendance.objects.get(pk=kwargs['pk'])
            attendance.has_evaluation_professional = True
            attendance.save()
            object = ProfessionalEvaluation(attendance=attendance, professional=attendance.professional)
            object.description = serializer['description']
            object.rating = 5
            rating_types = serializer['rating']
            # evaluation_type = EvaluationType.objects.get(pk=serializer['evaluation_type'])
            # object.evaluation_type = evaluation_type
            object.save()
            for rating_type in rating_types:
                new_object = ProfessionalEvaluation(attendance=attendance, professional=attendance.professional)
                new_object.evaluation_type_id = rating_type['id']
                icon = rating_type['icon']
                new_object.customer_choice = icon
                if icon == 'mood-bad':
                    new_object.rating = 1
                elif icon == 'sentiment-dissatisfied':
                    new_object.rating = 2
                elif icon == 'sentiment-neutral':
                    new_object.rating = 3
                elif icon == 'sentiment-satisfied':
                    new_object.rating = 4
                elif icon == 'mood':
                    new_object.rating = 5
                new_object.save()
            return Response(response, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfessionalHome(generics.GenericAPIView):
    """
    Returns the information displayed in the home screen of the Professional App
    """
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request):
        professional = Professional.objects.get(user=request.user)
        response = {}
        today = date.today()
        data_inicio = today - timedelta(days=7)
        lista_final = []
        payments = Transaction.objects.filter(attendance__professional=professional, type='professional').values()
        payments_historic = []
        lista = list(rrule.rrule(rrule.DAILY, interval=1, count=8, dtstart=data_inicio))
        for data in lista:
            transaction = Transaction.objects.filter(attendance__professional=professional, created__date=data.date(),
                                                     type='professional').aggregate(y=Sum('price'))
            if transaction['y']:
                payments_historic.append({'date': str(data.date()), 'total': transaction['y']})
            else:
                payments_historic.append({'date': str(data.date()), 'total': 0})
        response['payments_historic'] = payments_historic
        total = Transaction.objects.filter(attendance__professional=professional, type='professional',
                                           created__date__gte=data_inicio).aggregate(y=Sum('price'))
        if total['y']:
            response['total'] = total['y']
        else:
            response['total'] = 0
        response['payment_day'] = str(today + timedelta((1 - today.weekday()) % 7))
        response['rating'] = professional.rating
        response['news'] = []
        news = News.objects.all().order_by('-created')
        if news:
            response['news'] = serializers.NewsSerializer(news[0], context={'request': request}).data
        return Response(response, status=status.HTTP_200_OK)


class ProfessionalEvaluationApi(generics.GenericAPIView):
    """
    Returns the Professional Evaluation information in the Professional App
    """
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request):
        response = {}
        professional = Professional.objects.get(user=request.user)
        response['rating'] = professional.rating
        response['attendance_completed_count'] = Attendance.objects.filter(professional=professional, status='completed').count()
        response['evaluation_maximum'] = ProfessionalEvaluation.objects.filter(professional=professional,
                                                                               rating=5, evaluation_type__isnull=True).count()
        response['evaluations'] = list(professional.get_evaluations)
        evaluation_types = []
        evaluations_count = ProfessionalEvaluation.objects.filter(professional=professional,
                                                                  evaluation_type__isnull=False).count()
        if evaluations_count > 0:
            evaluations = ProfessionalEvaluation.objects.filter(professional=professional,
                                                                evaluation_type__isnull=False) \
                .values('evaluation_type__id').annotate(y=Count('id'),sum=Sum('rating'))
            for evaluation in evaluations:
                evaluation_type = EvaluationType.objects.get(pk=evaluation['evaluation_type__id'])
                evaluation_type = serializers.EvaluationTypeSerializer(evaluation_type,
                                                                       context={'request': request}).data
                evaluation_type['percent'] = int(evaluation['sum'] / (evaluation['y']*5) * 100)
                evaluation_types.append(evaluation_type)
        response['evaluation_types'] = evaluation_types
        return Response(response, status=status.HTTP_200_OK)


class ProfessionalSheddule(generics.GenericAPIView):
    """
    Lists Professional Schedule in the Professional App
    """
    permission_classes = [TokenHasReadWriteScope]

    def get(self, request):
        schedules = []
        dates = []
        professional = Professional.objects.get(user=request.user)
        today = datetime.now().date()
        professional_sheddules = Schedule.objects.select_related('attendance','attendance__customer__user',
                                                                 'attendance__initial_service')\
            .filter(professional=professional, daily_date__gte=today).order_by('daily_date','daily_time_begin')
        for professional_sheddule in professional_sheddules:
            hourlist = []
            attendance = {}
            date = professional_sheddule.daily_date
            if professional_sheddule.attendance:
                attendance['id'] = professional_sheddule.attendance.pk
                attendance['customer'] = professional_sheddule.attendance.customer.user.first_name
                attendance['service'] = professional_sheddule.attendance.initial_service.name
            hourlist.append({'hour_initial': professional_sheddule.daily_time_begin,
                             'hour_final': professional_sheddule.daily_time_end,
                             'attendance': attendance})
            if date in dates:
                for i in schedules:
                    if i['date'] == date:
                        schedules[len(dates) - 1]['hours'] = schedules[len(dates) - 1]['hours'] + hourlist
            else:
                dates.append(date)
                schedules.append({'date': date, 'hours': hourlist})
        return Response(schedules, status=status.HTTP_200_OK)


class CelphoneAPI(generics.GenericAPIView):
    """
    Sends a verification code to the Customer by SMS with the phone number given in the Customer App
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.CelphoneCustomer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        response = {}
        if serializer.is_valid():
            customer = Customer.objects.filter(user=request.user)
            customer = customer[0]
            phone = serializer.data['celphone']
            if phone != '10929207868':
                customer.celphone = serializer.data['celphone']
                customer.save()
                sms_code = generator_code()
                sms = Sms()
                data = {'to': str(55) + serializer.data['celphone'], 'from': 'BIURI', 'msg': 'codigo: ' + sms_code}
                sms.send(data=data)
            else:
                sms_code = '7478'
            response['sms_code'] = sms_code
            return Response(response, status=status.HTTP_200_OK)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceProfessionalPricingCriterionAPI(generics.ListCreateAPIView):
    """
    Allows the Professional to edit their own Pricing Criterion for a Service in the Professional App
    """
    # permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.ServiceProfessionalPricingCriterionGetSerializer
    queryset = ServiceProfessional.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.ServiceProfessionalPricingCriterionPostSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        attendance = Attendance.objects.get(pk=self.kwargs['pk'])
        # attendance_service = AttendanceService.objects.filter(attendance=attendance).values_list('service_id')
        queryset = self.queryset.filter(professional=attendance.professional)
        return queryset


    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        attendance = Attendance.objects.get(pk=self.kwargs['pk'])
        if serializer.is_valid():
            data = serializer.data['services']
            services_list = [i['id'] for i in data]
            services_sum = ServiceProfessional.objects.filter(pk__in=services_list).aggregate(y=Sum('average_time'))
            if 'y' in services_sum:
                if services_sum['y'] is not None:
                    c = Calendar()
                    if not attendance.expected_date_checkout:
                        expected_date_checkout = attendance.scheduling_date + timedelta(minutes=attendance.total_duration)
                    else:
                        expected_date_checkout = attendance.expected_date_checkout
                    disponibility = c.has_disponibility(professional=attendance.professional.pk,
                                                    date=attendance.scheduling_date.date(),
                                                    hour_inicial= expected_date_checkout.time() ,
                                                    hour_final=(expected_date_checkout+ timedelta(minutes=services_sum['y'])).time())
                    if disponibility:
                        services_attendance = AttendanceService.objects.filter(attendance=attendance)
                        if not services_attendance:
                            attendanceservice = AttendanceService(attendance=attendance,
                                                                  service=attendance.initial_service)
                            professional_service = ServiceProfessional.objects.get(service=attendance.initial_service,
                                                                                   professional=attendance.professional)
                            if not attendance.pricing_criterion_option:
                                attendanceservice.price = professional_service.minimum_price
                            else:
                                professional_pricing_criterion = ServiceProfessionalPricingCriterion.objects.get(
                                    service_professional=professional_service,
                                    pricingcriterionoptions=attendance.pricing_criterion_option)
                                attendanceservice.price = professional_pricing_criterion.price
                            attendanceservice.duration = professional_service.average_time
                            attendanceservice.save()
                        for item in data:
                            professional_service = ServiceProfessional.objects.get(pk=item['id'])
                            attendanceservice = AttendanceService(attendance=attendance,
                                                                  service=professional_service.service)
                            attendanceservice.price = professional_service.minimum_price
                            attendanceservice.duration = professional_service.average_time
                            attendanceservice.save()
                        attendance = Attendance.objects.get(pk=self.kwargs['pk'])
                        if not attendance.status in ['waiting_confirmation', 'draft', 'completed_draft']:
                            schedule = Schedule.objects.get(attendance=attendance)
                            schedule.daily_time_end = attendance.expected_date_checkout.time()
                            schedule.save()
                            c.process_full_calendar(attendance.professional.pk,attendance.scheduling_date.date())
                            process_scheduling_shock_calendar(professional=attendance.professional.pk)
                        serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    else:
                        return Response({'error': 'O profissional não tem disponibilidade na agenda'},
                                        status=status.HTTP_400_BAD_REQUEST)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ServiceProfessionalPricingCriterionAPIDelete(generics.DestroyAPIView):
    """
    Allows the Professional to delete their own Pricing Criterion for a Service in the Professional App
    """
    # permission_classes = [TokenHasReadWriteScope]
    queryset = AttendanceService.objects.all()

    def delete(self, request, *args, **kwargs):
        service = get_object_or_404(AttendanceService,pk=kwargs['pk'])
        attendance_id = service.attendance_id
        service.delete()
        attendance = Attendance.objects.select_related(
            'customer__user', 'professional__user', 'initial_service__category', 'credit_card', 'customer__user',
            'address',
            'pricing_criterion_option__pricing_criterion', 'neighborhood__city').get(pk=attendance_id)
        serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ServiceProfessionalAttendanceAPI(generics.ListCreateAPIView):
    """
    Lists the available Extra Services for an Attendance in the Customer App
    """
    # permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.ServiceProfessionalPricingCriterionGetSerializer
    queryset = ServiceProfessional.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.ServiceProfessionalPricingCriterionPostSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        if self.request.method == "GET":
            queryset = self.queryset.filter(
                professional_id=self.kwargs['pk'],
                enabled=True)
        else:
            queryset = self.queryset.filter(professional_id=self.kwargs['pk'])
        return queryset

class ServiceProfessionalAPI(APIView):

    def get_queryset(self):
        return ServiceProfessional.objects.filter(
            professional__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return serializers.ServiceProfessionalAPIGetSerializer
        else:
            return serializers.ServiceProfessionalAPIGetSerializer

    def get_object(self, obj_id):
        try:
            return self.get_queryset().get(id=obj_id)
        except (ServiceProfessional.DoesNotExist, ValidationError):
            raise status.HTTP_400_BAD_REQUEST

    def validate_ids(self, id_list):
        for id in id_list:
            try:
                self.get_queryset().get(id=id, )
            except (ServiceProfessional.DoesNotExist, ValidationError):
                raise status.HTTP_400_BAD_REQUEST
        return True

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer_class()
        serializer = serializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        id_list = request.data['ids']
        enabled_value = request.data['enabled']
        self.validate_ids(id_list=id_list)
        instances = []
        for id in id_list:
            obj = self.get_object(obj_id=id)
            obj.enabled = enabled_value
            obj.save()
            instances.append(obj)
        serializer = self.get_serializer_class()
        serializer = serializer(instances, many=True)
        return Response(serializer.data)


class CancelationAttendanceApi(generics.ListCreateAPIView):
    """
    Allows the user to Cancel an Attendance in either App
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.CancelationReasonSerializer
    queryset = CancelationReason.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.AttendanceCancelationSerializer
        else:
            return self.serializer_class

    def get_queryset(self):
        attendance = get_object_or_404(Attendance,pk=self.kwargs['pk'])
        queryset = self.queryset
        is_rejection = self.request.query_params.get('is_rejection', None)
        if is_rejection is not None:
            queryset = queryset.filter(is_rejection=is_rejection)
        user = self.request.user
        customer = Customer.objects.filter(user=user)
        professional = Professional.objects.filter(user=user)
        if customer.exists():
            return queryset.filter(type='customer')
        if professional.exists():
            return queryset.filter(type='professional')

    def post(self, request, *args, **kwargs):
        attendance = get_object_or_404(Attendance, pk=kwargs['pk'])
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            attendance.status = data.get('status')
            attendance.save()
            cancelation_reason_id = data.get('cancelation_reason')
            obs = data.get('obs', None)
            cancelation_reason = CancelationReason.objects.get(pk = cancelation_reason_id)
            attendance_cancelation = AttendanceCancelation.objects.filter(attendance=attendance)
            if attendance_cancelation.exists():
                attendance_cancelation = attendance_cancelation.first()
            else:
                attendance_cancelation = AttendanceCancelation(attendance=attendance)
            attendance_cancelation.cancelation_reason = cancelation_reason
            attendance_cancelation.type = cancelation_reason.type
            attendance_cancelation.is_rejection = cancelation_reason.is_rejection
            attendance_cancelation.obs = obs
            attendance_cancelation.save()
            attendance_serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
            return Response(attendance_serializer.data,status=status.HTTP_200_OK)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EvaluationFinalProfessional(generics.GenericAPIView):
    """
    Allows the Customer to evaluate a Professional in the current Attendance
    """
    serializer_class = serializers.EvaluationFinalProfessional

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        attendance = Attendance.objects.get(pk=self.kwargs['pk'])
        id = None
        if serializer.is_valid():
            evaluation_customer = EvaluationCustomer.objects.filter(attendance=attendance)
            if evaluation_customer:
                id = evaluation_customer.first().pk
            if id is not None:
                serializer.update(instance=EvaluationCustomer.objects.get(id=id), validated_data=serializer.data)
            else:
                serializer.save(attendance=attendance)
            attendance.has_evaluation = True
            attendance.save()
            return Response(status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfessionalShedduleUpdate(generics.ListCreateAPIView):
    """
    Allows the Professional to update their Schedule in the Professional App
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.ProfessionalScheduleSerializer

    def get_queryset(self):
        schedule = ProfessionalSchedule.objects.filter(professional__user=self.request.user)
        return schedule

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data.get('id', None)
            date_schedule = serializer.validated_data.get('date_schedule')
            sheddule = ProfessionalSchedule.objects.filter(professional__user=self.request.user,
                                                           date_schedule=date_schedule)
            if sheddule:
                id = sheddule.first().pk
            if id is not None:
                serializer.update(instance=ProfessionalSchedule.objects.get(id=id), validated_data=serializer.data)
            else:
                serializer.save(professional=Professional.objects.get(user=self.request.user))
            list_sheddule = ProfessionalSchedule.objects.filter(professional__user=self.request.user)
            response = serializers.ProfessionalScheduleSerializer(list_sheddule, context={'request': request},
                                                                  many=True).data
            return Response(response, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfessionalBankAccount(generics.ListCreateAPIView):
    """
    Returns the Bank Account Data in the Professional App
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.ProfessionalBankSerializer

    def get_queryset(self):
        professional = Professional.objects.get(user=self.request.user)
        bankaccount = BankAccount.objects.filter(pk=professional.bank_account.pk)
        return bankaccount

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            professional = Professional.objects.get(user=self.request.user)
            bankaccount = BankAccount.objects.get(pk=professional.bank_account.pk)
            serializer.update(instance=bankaccount, validated_data=serializer.data)
            return Response({}, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteProfessionalApi(generics.ListCreateAPIView):
    """
    Lists the Favorite Professionals for a Customer in the Customer App
    """
    permission_classes = [TokenHasReadWriteScope]
    serializer_class = serializers.ProfessionalSerializer

    def get_queryset(self):
        professional = Professional.objects.filter(
            customer_favorites__customer__user=self.request.user,
            customer_favorites__is_removed=False)
        return professional

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.FavoriteProfessionalPost
        else:
            return self.serializer_class

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            id = serializer.validated_data.get('id')
            is_favorite = serializer.validated_data.get('is_favorite')
            professional = get_object_or_404(Professional, pk=id)
            customer = get_object_or_404(Customer, user=self.request.user)
            object = FavoriteProfessional.objects.get_or_create(customer=customer, professional=professional)[0]
            if not is_favorite:
                object.delete()
            return Response({}, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AttendanceVoucher(generics.GenericAPIView):
    """
    Validates and Applies the Voucher to an Attendance in the Customer App
    """

    serializer_class = serializers.VoucherSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        attendance = Attendance.objects.get(pk=self.kwargs['pk'])
        if serializer.is_valid():
            voucher = get_object_or_404(Voucher,code__iexact=serializer.validated_data.get('code'))
            voucher_validate = voucher.validate_voucher(customer_id=attendance.customer_id,
                                     service_id=attendance.initial_service_id,
                                     attendance_value=attendance.total_price,
                                     attendance_scheduling_date=attendance.scheduling_date)
            if voucher_validate['is_valid']:
                attendance.total_discount = voucher_validate['discount_value']
                attendance.voucher = voucher
                attendance.save()
                voucher.use_voucher(customer_id=attendance.customer_id)
            else:
                return Response({}, status=status.HTTP_404_NOT_FOUND)
            serializer = serializers.AttendanceSerializer(attendance, context={'request': request})
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LeadProfessionalApi(generics.CreateAPIView):
    """
    Allows the user to send a Professional Lead from either App
    """
    serializer_class = serializers.ProfessionalLeadSerializer
    #permission_classes = [TokenHasReadWriteScope]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = self.request.user
            lead = serializer.save()
            if not user.is_anonymous():
                customer = Customer.objects.filter(user=user)
                professional = Professional.objects.filter(user=user)
                lead.indicated_by = user
                obs = ''
                if customer.exists():
                    customer = customer[0]
                    obs = 'Indicado pelo cliente: {} telefone: {}'.format(customer.user.first_name, customer.celphone)
                if professional.exists():
                    professional = professional[0]
                    obs = 'Indicado pelo profissional: {} telefone: {}'.format(professional.user.first_name, professional.celphone)
            else:
                obs = 'Pedido de pré-cadastramento no App'
            lead.obs = obs
            lead.save()
            return Response({}, status=status.HTTP_201_CREATED)
        print("DEBUG: serializer_400={}".format(str(serializer)))
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionListApi(generics.ListAPIView):
    """
    Lists the Transactions for the current User in the Professional App
    """
    serializer_class = serializers.TransactionSerializer
    queryset = Transaction.objects.select_related('attendance','attendance__address','attendance__customer__user')\
        .prefetch_related('attendance__services').filter(type='professional')
    permission_classes = [TokenHasReadWriteScope]
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = '__all__'

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(attendance__professional__user=self.request.user)
        date_begin = self.request.query_params.get('date_begin', None)
        date_end = self.request.query_params.get('date_end', None)
        if date_begin is None or date_begin == '':
            date_begin = datetime.today() - timedelta(days=7)
        queryset = queryset.filter(created__date__gte=date_begin)
        if date_end is not None:
            if date_end != '':
                queryset = queryset.filter(created__date__lte=date_end)
        return queryset


class TransactionDetailApi(generics.RetrieveAPIView):
    """
    Details the chosen Transaction in the Professional App
    """
    serializer_class = serializers.TransactionSerializer
    queryset = Transaction.objects.select_related('attendance','attendance__address','attendance__customer__user','bank_account')\
        .prefetch_related('attendance__services').filter(type='professional')
    permission_classes = [TokenHasReadWriteScope]

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(attendance__professional__user = self.request.user)

class PlainTextParser(BaseParser):
        """
        Plain text parser.
        """
        media_type = 'text/plain'

        def parse(self, stream, media_type=None, parser_context=None):
            """
            Simply return a string representing the body of the request.
            """
            return stream.read()


class IuguWebhookApi(generics.GenericAPIView):

    parser_classes = (PlainTextParser,)

    def post(self, request, *args, **kwargs):
        from urllib import parse
        query_params = dict(parse.parse_qsl(request.data.decode("utf-8").replace('\n','')))
        if 'event' in query_params:
            event = query_params['event']
            if event == 'referrals.verification':
                account_id = query_params['data[account_id]']
                account_status = query_params['data[status]']
                professional = Professional.objects.filter(iugu_account_id=account_id)
                if professional.exists():
                    professional = professional[0]
                    if account_status == 'accepted':
                        professional.professional_verified = True
                    elif account_status == 'rejected':
                        professional.professional_verified = False
                        professional.observation += '\nPendencia Iugu: ' + query_params['data[feedback]']
                    professional.save()
                else:
                    pass
            elif event == 'withdraw_request.status_changed':
                withdraw_request_id = query_params['data[withdraw_request_id]']
                withdraw_status = query_params['data[status]']
                observation = ''
                if 'data[feedback]' in query_params:
                    observation = query_params['data[feedback]']
                transfer = Transfer.objects.filter(transfer_iugu_id=withdraw_request_id)
                if transfer.exists():
                    transfer = transfer[0]
                    transfer.status = withdraw_status
                    transfer.observation = observation
                    transfer.save()
        return Response({}, status=status.HTTP_202_ACCEPTED)


class ServiceProfessionalListApi(generics.ListCreateAPIView):
    """
    Lists the Services for the user in the Professional App
    """
    serializer_class = serializers.ServiceProfessionalSerializer
    permission_classes = [TokenHasReadWriteScope]
    queryset = ServiceProfessional.objects.select_related('service__category')
    filter_backends = (filters.OrderingFilter,)
    ordering = ['service__category__name', 'service__name']

    def get_serializer_class(self):
        if self.request.method == "POST":
            return serializers.ServiceProfessionalPostSerializer
        else:
            return self.serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        service = ServiceProfessional(service_id=serializer.data['service'],
                                      minimum_price = serializer.data['minimum_price'],
                                      average_time=serializer.data['average_time'],
                                      professional=Professional.objects.get(user=self.request.user))
        service.save()
        return Response(status=status.HTTP_201_CREATED)

    def get_queryset(self):
        return super().get_queryset().filter(professional__user=self.request.user)


class AttendanceSplitApi(generics.GenericAPIView):
    """
    Allows the Customer to set Splits for the Attendance Payment in the Customer App
    """
    serializer_class = serializers.SplitSerializer
    # permission_classes = [TokenHasReadWriteScope]

    def get(self, request, *args, **kwargs):
        attendance = get_object_or_404(Attendance, pk=kwargs['pk'])
        serializer = self.serializer_class(attendance.split_payments, context={'request': request}, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ServiceProfessionalDetailApi(generics.RetrieveUpdateDestroyAPIView):
    """
    Allows the Professional to edit the Details of a Service in the Professional App
    """
    serializer_class = serializers.ServiceProfessionalSerializer
    permission_classes = [TokenHasReadWriteScope]
    queryset = ServiceProfessional.objects.select_related('service__category')


class NewAttendance(generics.GenericAPIView):
    """
    Creates a new Attendance based on another in the Customer App
    """
    serializer_class = None
    permission_classes = [TokenHasReadWriteScope]

    def post(self, request, *args, **kwargs):
        attendance = get_object_or_404(Attendance, pk=kwargs['pk'])
        dict_attendance = attendance.__dict__
        new_dict_attendance = {}
        for key, value in dict_attendance.items():
            if not key.startswith('_'):
                new_dict_attendance[key] = value
        new_dict_attendance['status'] = 'draft'
        new_dict_attendance['id'] = None
        new_attendance = Attendance(**new_dict_attendance)
        if new_attendance.scheduling_date < datetime.now():
            new_attendance.scheduling_date = None
        new_attendance.save()
        attendance_serializer = serializers.AttendanceSerializer(new_attendance, context={'request': request})
        return Response(attendance_serializer.data,status=status.HTTP_200_OK)



class LastServices(BestPraticsList, generics.ListAPIView):
    """
    Show last 10 attendances at the main page
    """

    queryset = Attendance.objects.select_related(
                                             'customer__user', 'professional__user','initial_service__category',
                                             'credit_card','customer__user','address',
                                             'pricing_criterion_option__pricing_criterion')\
                                             .prefetch_related('attendance_relation__service__category')
    serializer_class = serializers.AttendanceSerializer
    pagination_class = LastAttendancesPagination
    ordering_fields = ['-id']


    def get_queryset(self):
        query = self.queryset.exclude(status__in=['draft', 'completed_draft'])
        query_params = self.request.query_params
        historic = query_params.get('historic', None)
        status = query_params.get('status', None)
        customer_id = query_params.get('customer', None)
        customer = Customer.objects.filter(id=customer_id)
        if customer.exists():
            if historic is not None:
                if historic == 'true':
                    query = query.filter(
                        Q(status__in=['completed'])).order_by('-id')
            # else:
            #     if historic == 'true':
            #         ordering = 'completed_date'
            #         query = query.exclude(
            #             Q(status__in=['completed']))

        return query
    

class ToggleServices(APIView):

    def get_queryset(self):
        return ServiceProfessional.objects.filter(
            professional__user=self.request.user)

    def get_object(self, obj_id):
        try:
            return self.get_queryset().get(id=obj_id)
        except (ServiceProfessional.DoesNotExist, ValidationError):
            raise status.HTTP_400_BAD_REQUEST

    def validate_ids(self, id_list):
        for id in id_list:
            try:
                self.get_queryset().get(id=id, )
            except (ServiceProfessional.DoesNotExist, ValidationError):
                raise status.HTTP_400_BAD_REQUEST
        return True

    def patch(self, request, pk, *args, **kwargs):
        complete_date_end = parser.isoparse(request.data['complete_date_end'])
        # date_start = parser.isoparse(request.data['date_start'])
        service = ServiceProfessional.objects.get(pk=pk)
        obj = SaloonScheduleRemove.objects.create(
            service_professional = service,
            daily_time_begin = request.data['date_start'],
            daily_time_end = request.data['date_end'],
            daily_date= request.data['day'],
            professional = Professional.objects.get(user=request.user)
        )
        reEnableService.apply_async((obj.id,), eta=complete_date_end)
        return Response(status=status.HTTP_200_OK)

class ScheduleRemoveViewSet(viewsets.ModelViewSet):

    class ScheduleRemoveSerializer(ModelSerializer):

        service_professional = serializers.ServiceProfessionalSerializer()

        class Meta:
            model = SaloonScheduleRemove
            fields = ['id', 'daily_time_begin', 'daily_time_end', 'daily_date', 'complete_date_end', 'service_professional']

    serializer_class = ScheduleRemoveSerializer

    def get_queryset(self):
        return SaloonScheduleRemove.objects.filter(professional__user=self.request.user)