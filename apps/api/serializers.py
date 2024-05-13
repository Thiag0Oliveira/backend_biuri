from datetime import timedelta, datetime
from dateutil.parser.isoparser import isoparse
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.utils.translation import ugettext_lazy as _

from allauth.account import app_settings
from allauth.account.adapter import get_adapter
from allauth.account.app_settings import AuthenticationMethod
from allauth.account.forms import default_token_generator
from allauth.account.utils import (
    filter_users_by_email, setup_user_email, user_pk_to_url_str, user_username
)
from allauth.utils import build_absolute_uri
from oauth2_provider.models import Application
from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from apps.common.models import UserAddress
from apps.core.models import State, City, Neighborhood
from apps.customer.models import Customer
from apps.lead_captation.models import ExecutiveLead, ProfissionalLead
from apps.message_core.models import News
from apps.payment.models import BANCOS, BankAccount, CreditCard, Transaction, Voucher
from apps.payment.views import split_text_generate
from apps.professional.models import (
    GENDER_LIST, Badge, Calendar, EvaluationCustomer, EvaluationType, Professional, ProfessionalBadge,
    ProfessionalEvaluation, ProfessionalSchedule, Schedule, ServiceProfessional, SaloonScheduleRemove,
    ServiceProfessionalPricingCriterion, ServiceProfessionalLog
)
from apps.service_core.models import (
    Attendance, AttendanceService, Category, PricingCriterion, PricingCriterionOptions, Service,
    CancelationReason, AttendanceCancelation)


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        fields = self.context['request'].query_params.get('fields')
        if fields:
            fields = fields.split(',')
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ExecutiveLeadSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = ExecutiveLead
        fields = '__all__'


class ProfessionalLeadSerializer(DynamicFieldsModelSerializer):
    telephone = serializers.CharField(required=True, max_length=11)

    class Meta:
        model = ProfissionalLead
        fields = ['name', 'telephone',]


class SignUpSerializer(RegisterSerializer):
    name = serializers.CharField()

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        name = request.data['name'].split(' ')
        user.first_name = name[0]
        print("Entramos no serializer")
        if len(name) > 1:
            len_last_name = len(name[0]) + 30
            user.last_name = request.data['name'][:len_last_name].replace(name[0],'')
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    professional = serializers.BooleanField(default=False, required=False)

    def validate(self, data):
        email = get_adapter().clean_email(data['email'])
        professional = data['professional']
        app = Application.objects.all()
        if professional:
            professional = Professional.objects.filter(user__email__iexact=email.lower())
            if not professional.exists():
                raise serializers.ValidationError({"error": _("The e-mail address is not assigned"
                                                                  " to any user account"), "status": "error"})
        else:
            customer = Customer.objects.filter(user__email__iexact=email.lower())
            if not customer.exists():
                raise serializers.ValidationError({"error": _("The e-mail address is not assigned"
                                                                  " to any user account"), "status": "error"})
        if not app:
            raise serializers.ValidationError({"error": _("The app is not setting"), "status": "error"})
        return data


class CreditCardGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditCard
        fields = '__all__'


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data['email']
        email = get_adapter().clean_email(email)
        self.users = filter_users_by_email(email)
        return data

    def save(self, request, **kwargs):
        current_site = get_current_site(request)
        email = self.validated_data['email']
        token_generator = kwargs.get("token_generator",
                                     default_token_generator)

        customer = Customer.objects.filter(user__email__iexact=email.lower())

        if customer.exists():
            user = customer[0].user

            temp_key = token_generator.make_token(user)

            path = reverse("account_reset_password_from_key",
                           kwargs=dict(uidb36=user_pk_to_url_str(user),
                                       key=temp_key))
            url = build_absolute_uri(
                request, path)

            context = {"current_site": current_site,
                       "user": user,
                       "password_reset_url": url,
                       "request": request}

            if app_settings.AUTHENTICATION_METHOD \
                    != AuthenticationMethod.EMAIL:
                context['username'] = user_username(user)
            get_adapter(request).send_mail(
                'account/email/password_reset_key',
                email,
                context)


class NotificationSerializer(serializers.Serializer):
    to = serializers.CharField(required=True)
    title = serializers.CharField(required=True)
    body = serializers.CharField(required=True)


class ConvertTokenSerializer(serializers.Serializer):
    key = serializers.CharField(required=True, max_length=100)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Service
        fields = '__all__'


class VoucherModelSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voucher
        fields = ['id', 'code', 'campaign', 'discount']


class AttendanceServiceSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = AttendanceService
        fields = ('id', 'price', 'duration', 'service')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name')


class ProfileUpdateSerializer(serializers.ModelSerializer):
    birthday = serializers.DateField()
    gender = serializers.ChoiceField(choices=GENDER_LIST)
    celphone = serializers.CharField()
    avatar = serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'birthday', 'gender', 'celphone', 'avatar')


class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    avatar = serializers.URLField(source='get_avatar')

    class Meta:
        model = Customer
        fields = ('id', 'user', 'avatar', 'birthday', 'gender', 'celphone')


class ProfessionalSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Professional
        fields = ('id', 'user', 'avatar', 'attendance_completed_count', 'rating', 'birthday', 'gender', 'celphone')


class ProfessionalSerializerListAttentance(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    price = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()

    class Meta:
        model = Professional
        fields = ('id', 'user', 'avatar', 'attendance_completed_count', 'rating', 'price', 'is_favorite')

    def get_price(self, obj, *args, **kwargs):
        service_professional = ServiceProfessional.objects.filter(professional_id=obj.pk,
                                                                  service=self.context['service'])
        pricing_criterion_option = self.context['pricing_criterion_option']
        if pricing_criterion_option is not None:
            service_criterion = ServiceProfessionalPricingCriterion.objects.filter(service_professional=service_professional,
                                                                       pricingcriterionoptions=pricing_criterion_option)
            if service_criterion.exists():
                price = service_criterion[0].price
            else:
                price = service_professional[0].minimum_price
        else:
            price = service_professional[0].minimum_price
        return str(round(price, 2))

    def get_is_favorite(self, obj, *args, **kwargs):
        if obj.pk in self.context['professional_favorites']:
            return True
        return False


class PricingCriterionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PricingCriterion
        fields = ('id', 'description')


class PricingCriterionOptionsSerializer(serializers.ModelSerializer):
    pricing_criterion = PricingCriterionSerializer(read_only=True)

    class Meta:
        model = PricingCriterionOptions
        fields = ('id', 'description', 'pricing_criterion')


class AttendancePricingCriterionSerializer2(serializers.ModelSerializer):
    class Meta:
        model = PricingCriterionOptions
        fields = ('id', 'description')


class AttentancePricingCriterionSerializer(serializers.ModelSerializer):
    options = AttendancePricingCriterionSerializer2(many=True, read_only=True, source='get_options')

    class Meta:
        model = PricingCriterion
        fields = ('id', 'description','picture_male', 'picture_female', 'options')


class UserAddressSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())
    name = serializers.CharField(max_length=200, allow_blank=True, required=False)
    postal_code = serializers.CharField(max_length=8, min_length=8)
    address = serializers.CharField(max_length=200)
    complemento = serializers.CharField(max_length=100, allow_blank=True, required=False)
    number = serializers.CharField(max_length=120)
    neighborhood = serializers.CharField(max_length=120)
    city = serializers.CharField(max_length=120)
    state = serializers.CharField(max_length=120)

    class Meta:
        model = UserAddress
        exclude = ('user', 'is_removed')


class NeighborhoodSerializer(serializers.ModelSerializer):

    class Meta:
        model = Neighborhood
        fields = ('id', 'description')


class AttendanceSerializer(serializers.HyperlinkedModelSerializer):
    services = AttendanceServiceSerializer(many=True, read_only=True, source='attendance_relation')
    customer = CustomerSerializer()
    professional = ProfessionalSerializer(read_only=True)
    pricing_criterion_option = PricingCriterionOptionsSerializer()
    initial_service = ServiceSerializer()
    address = UserAddressSerializer()
    neighborhood = NeighborhoodSerializer()
    credit_card = CreditCardGetSerializer(read_only=True)
    voucher = VoucherModelSerializer(read_only=True)
    total_price = serializers.DecimalField(source='get_total_price', max_digits=10, decimal_places=2)
    factor = serializers.DecimalField(max_digits=3, decimal_places=2)
    split_text = serializers.SerializerMethodField()
    ## Horário do início do período de atendimento flexível
    flexible_date_start = serializers.DateTimeField()
    ## Horário do fim do período de atendimento flexível
    flexible_date_end = serializers.DateTimeField()

    def get_split_text(self, obj):
        print("DEBUG: serializer get_split_text, obj={}".format(repr(obj)))
        ## Atendimento agendado
        if obj.flexible_discount > 0.0:
            split = round((float(obj.total_price) * float(obj.flexible_discount) + float(obj.total_interest) - float(obj.total_discount)) / float(obj.splits_number), 2)
        else:
            split = round((float(obj.total_price) + float(obj.total_interest) - float(obj.total_discount)) / float(obj.splits_number), 2)
        return split_text_generate(obj.splits_number,split)

    def validate_status(self, value):
        ## FIXME estes erros não estão sendo tratados pelo aplicativo
        print("DEBUG: serializer validate_status, value={}".format(repr(value)))
        attendance = self.instance
        ## Atendimento flexível
        if not attendance.scheduling_date and attendance.flexible_date_start:
            attendance.scheduling_date = attendance.flexible_date_start
        c = Calendar()
        if value == 'waiting_confirmation':
            print("DEBUG: waiting_confirmation")
            attendances_pending = Attendance.objects.filter(customer=attendance.customer, status='pending_payment')
            if attendances_pending.exists():
                print("DEBUG: ", "Existem atendimentos com problema de pagamento")
                raise serializers.ValidationError("Existem atendimentos com problema de pagamento")
            if not attendance.address:
                print("DEBUG: ", "Endereço Não informado")
                raise serializers.ValidationError("Endereço Não informado")
            elif not attendance.credit_card:
                print("DEBUG: ", "Cartão de crédito não informado")
                raise serializers.ValidationError("Cartão de crédito não informado")
            elif not attendance.scheduling_date:
                print("DEBUG: ", "Informe o horário de agendamento")
                raise serializers.ValidationError("Informe o horário de agendamento")
            elif attendance.initial_service.pricing_criterion:
                print("DEBUG: attendance.initial_service.pricing_criterion")
                if not attendance.pricing_criterion_option:
                    print("DEBUG: ", "Preencha as informações complementares")
                    raise serializers.ValidationError("Preencha as informações complementares")
            elif attendance.scheduling_date < datetime.now() + timedelta(hours=3):
                print("DEBUG: ", "O horário agendado não está mais disponível")
                raise serializers.ValidationError("O horário agendado não está mais disponível")
            ## Valida horários de agendamento de acordo com regras de negócio
            # if attendance.flexible_date_end - attendance.flexible_date_start < timedelta(hours=4):
            #     print("DEBUG: ", "A janela de horário para atendimento deve ser de no mínimo quatro horas")
            #     raise serializers.ValidationError("A janela de horário para atendimento deve ser de no mínimo quatro horas")
            if attendance.flexible_date_start:
                if attendance.flexible_date_start.day != attendance.flexible_date_end.day:
                    print("DEBUG: ", "A janela de horário para atendimento deve ser no mesmo dia")
                    raise serializers.ValidationError("A janela de horário para atendimento deve ser no mesmo dia")
            disponibility = True
            if attendance.professional:
                print("DEBUG: attendance.professional")
                disponibility = c.has_disponibility(professional=attendance.professional.pk,
                                                    date=attendance.scheduling_date.date(),
                                                    hour_inicial=attendance.scheduling_date.time(),
                                                    hour_final=((attendance.scheduling_date + timedelta(minutes=attendance.total_duration)).time()))
            elif not disponibility:
                print("DEBUG: ", "O horário agendado não está mais disponível")
                raise serializers.ValidationError("O horário agendado não está mais disponível")
            print("DEBUG: token...")
            token = attendance.charge()
            print("DEBUG: token={}".format(repr(token)))
            if not 'success' in token:
                print("DEBUG: ", "Pagamento não Aprovado. Verifique o cartão escolhido")
                raise serializers.ValidationError("Pagamento não Aprovado. Verifique o cartão escolhido")
            if 'success' in token:
                print("DEBUG: success")
                if not token['success']:
                    print("DEBUG: ", "Pagamento não Aprovado. Verifique o cartão escolhido")
                    raise serializers.ValidationError("Pagamento não Aprovado. Verifique o cartão escolhido")
        if value == 'complete_draft':
            print("DEBUG: complete_draft")
            disponibility = True
            if attendance.professional:
                print("DEBUG: attendance.professional")
                disponibility = c.has_disponibility(professional=attendance.professional.pk,
                                                    date=attendance.scheduling_date.date(),
                                                    hour_inicial=attendance.scheduling_date.time(),
                                                    hour_final=(attendance.scheduling_date.time() +
                                                                timedelta(minutes=attendance.total_duration)))
            if not attendance.address:
                print("DEBUG: ", "Endereço Não informado")
                raise serializers.ValidationError("Endereço Não informado")
            elif not attendance.credit_card:
                print("DEBUG: ", "Cartão de crédito não informado")
                raise serializers.ValidationError("Cartão de crédito não informado")
            elif attendance.initial_service.pricing_criterion:
                print("DEBUG: attendance.initial_service.pricing_criterion")
                if not attendance.pricing_criterion_option:
                    print("DEBUG: ", "Preencha as informações complementares")
                    raise serializers.ValidationError("Preencha as informações complementares")
            elif not disponibility:
                print("DEBUG: ", "O horário agendado não está mais disponível")
                raise serializers.ValidationError("O horário agendado não está mais disponível")
        return value

    class Meta:
        model = Attendance
        fields = ['id', 'status', 'completed_date', 'scheduling_date', 'total_duration', 'expected_date_checkout', 'total_price',
                  'total_discount', 'total_administrate_tax','total_interest','splits_number', 'observation', 'initial_service', 'address', 'services',
                  'customer', 'professional', 'pricing_criterion_option', 'credit_card', 'in_attendance_date', 'neighborhood',
                  'voucher', 'split_text', 'type', 'pixel_id', 'flexible_date_start', 'flexible_date_end', 'factor']
        read_only_fields = ('total_duration', 'total_price', 'total_discount', 'total_interest',
                            'total_administrate_tax', 'customer', 'in_attendance_date', 'split_text', 'type')
        optional_fields = ['factor', ]


class AttendanceCreateSerializer(serializers.Serializer):
    service = serializers.IntegerField(required=False)
    services = serializers.JSONField(required=False)
    professional = serializers.IntegerField(required=False)
    pixel_id = serializers.CharField(required=False)


class ToggleServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaloonScheduleRemove
        fields = ('daily_date', 'daily_time_begin', 'daily_time_end', 'service_professional')


class AttendanceUpdateSerializer(serializers.ModelSerializer):
    flexible_date_end = serializers.DateTimeField(required=True)
    flexible_date_start = serializers.DateTimeField(required=True)
    scheduling_date = serializers.DateTimeField(required=True)
    status = serializers.CharField(required=True)
    split_text = serializers.SerializerMethodField()
    # factor = serializers.DecimalField(max_digits=3, decimal_places=2)

    def get_split_text(self, obj):
        print("DEBUG: serializer get_split_text, obj={}".format(repr(obj)))
        ## Atendimento agendado
        if obj.flexible_discount > 0.0:
            split = round((float(obj.total_price) * float(obj.flexible_discount) + float(obj.total_interest) - float(obj.total_discount)) / float(obj.splits_number), 2)
        else:
            split = round((float(obj.total_price) + float(obj.total_interest) - float(obj.total_discount)) / float(obj.splits_number), 2)
        return split_text_generate(obj.splits_number,split)


    class Meta:
        model = Attendance
        fields = '__all__'

        read_only_fields = ('split_text', 'factor')
        optional_fields = ['factor', ]

class AttendanceAddressSerializer(serializers.Serializer):
    address = serializers.IntegerField(required=False)
    neighborhood = serializers.IntegerField(required=False)


class AttendanceCreditCardSerializer(serializers.Serializer):
    credit_card = serializers.IntegerField(required=True)


class AttendancePricingCriterionOptionsSerializer(serializers.Serializer):
    pricing_criterion_option = serializers.IntegerField(required=False)
    observation = serializers.CharField(required=True, allow_blank=True)


class AttendanceProfessionalSerializer(serializers.Serializer):
    professional = serializers.IntegerField(required=True)


class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = ('id', 'description', 'picture')


class ProfessionalBadgeSerializer(serializers.ModelSerializer):
    # badge = BadgeSerializer(read_only=True)

    class Meta:
        model = ProfessionalBadge
        fields = ('id', 'description')


class ProfessionalEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProfessionalEvaluation
        fields = ('id', 'description')


class ProfessionalDetailSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(read_only=True)
    badges = BadgeSerializer(many=True, read_only=True)
    instagram_pictures = serializers.JSONField(source='get_instagram_pictures')
    evaluations = serializers.JSONField(source='get_evaluations')
    category = CategorySerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField()

    def get_is_favorite(self, obj):
        if self.context['request'].user.is_anonymous():
            return False
        professionals = Professional.objects.filter(customer_favorites__customer__user=self.context['request'].user,
                                                    customer_favorites__is_removed=False)
        if obj in professionals:
            return True
        return False

    class Meta:
        model = Professional
        fields = ('id', 'user', 'avatar', 'description', 'category', 'attendance_completed_count', 'rating', 'badges',
                  'evaluations', 'instagram_pictures', 'is_favorite')


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('daily_date', 'daily_time_begin', 'daily_time_end')


class ProfessionalEvaluationPostSerializer(serializers.Serializer):
    description = serializers.CharField(allow_blank=True)
    rating = serializers.JSONField()


class CreditCardPostSerializer(serializers.Serializer):
    number = serializers.CharField()
    verification_value = serializers.CharField()
    name = serializers.CharField()
    month = serializers.CharField()
    year = serializers.CharField()


class AttendanceAcceptedPostSerializer(serializers.Serializer):
    status = serializers.CharField()


class AppRegistration(serializers.Serializer):
    registration_id = serializers.CharField(required=True, max_length=100)


class CelphoneCustomer(serializers.Serializer):
    celphone = serializers.CharField(required=True, max_length=11)


class EvaluationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationType
        exclude = ('is_removed',)


class ServiceProfessionalPricingCriterionGetSerializer(serializers.ModelSerializer):
    price = serializers.CharField(source='minimum_price')
    service = serializers.CharField(source='name_service')

    class Meta:
        model = ServiceProfessional
        fields = ('id', 'service', 'price')

class ServiceProfessionalAPIGetSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    
    class Meta:
        model = ServiceProfessional
        fields = '__all__'

class ServiceProfessionalAPIPatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = ServiceProfessional
        fields = ('id', 'enabled')


class ServiceProfessionalPricingCriterionPostSerializer(serializers.Serializer):
    services = serializers.JSONField()


class NewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = News
        exclude = ['is_removed', ]


class EvaluationFinalProfessional(serializers.ModelSerializer):
    observation = serializers.CharField(allow_blank=True)

    class Meta:
        model = EvaluationCustomer
        exclude = ['is_removed', 'created', 'modified', 'attendance', ]


class ProfessionalScheduleSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=False, required=False)

    class Meta:
        model = ProfessionalSchedule
        exclude = ['is_removed', 'professional', 'created', 'modified']


class ProfessionalBankSerializer(serializers.ModelSerializer):

    class Meta:
        model = BankAccount
        exclude = ['is_removed', 'created', 'modified']


class FavoriteProfessionalPost(serializers.Serializer):
    id = serializers.IntegerField()
    is_favorite = serializers.BooleanField()


class VoucherSerializer(serializers.Serializer):
    code = serializers.CharField()


class CancelationReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = CancelationReason
        fields = ['id', 'name', 'need_obs']


class AttendanceCancelationSerializer(serializers.Serializer):
    cancelation_reason = serializers.ModelField(model_field=AttendanceCancelation._meta.get_field('cancelation_reason'))
    obs = serializers.CharField(max_length=1000, required=False, allow_blank=True)
    status = serializers.CharField(max_length=30)

    # class Meta:
    #     fields = ['status','cancelation_reason','obs']


class AttendanceListMinimal(serializers.ModelSerializer):
    services = AttendanceServiceSerializer(many=True, read_only=True, source='attendance_relation')
    customer = CustomerSerializer()
    address = UserAddressSerializer()

    class Meta:
        model = Attendance
        fields = ['id', 'status', 'scheduling_date', 'total_duration', 'expected_date_checkout', 'total_price',
                  'total_discount', 'total_administrate_tax', 'observation', 'initial_service', 'address', 'services',
                  'customer', 'in_attendance_date']
        read_only_fields = (
            'total_duration', 'total_price', 'total_discount', 'total_administrate_tax', 'customer',
            'in_attendance_date')


class TransactionSerializer(serializers.ModelSerializer):
    attendance = AttendanceListMinimal()

    class Meta:
        model = Transaction

        fields = ['id', 'price', 'created', 'is_recebido', 'attendance']


class ServiceProfessionalSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    def validate_minimum_price(self, value):
        service_professional = self.instance
        last_modified_range = service_professional.modified + relativedelta(months=1)
        datetime_atual = datetime.now()
        service = service_professional.service
        if value < service.minimal_range_price:
            raise serializers.ValidationError("O preço mínimo para esse serviço é R${}".format(service.minimal_range_price))
        # if last_modified_range > datetime_atual:
        #     raise serializers.ValidationError("Modificação não permitida, você modificou há menos de 1 mês.")
        return value

    def update(self, instance, validated_data):
        service_log = ServiceProfessionalLog()
        service_log.professional = instance.professional
        service_log.service = instance.service
        service_log.maximum_price_old = instance.maximum_price
        service_log.minimum_price_old = instance.minimum_price
        service_log.average_time_old = instance.average_time
        if 'maximum_price' in validated_data:
            service_log.maximum_price = validated_data['maximum_price']
        else:
            service_log.maximum_price = instance.maximum_price
        service_log.minimum_price = validated_data['minimum_price']
        service_log.average_time = validated_data['average_time']
        service_log.save()
        return super().update(instance, validated_data)

    class Meta:
        model = ServiceProfessional
        fields = ['id', 'service', 'minimum_price', 'average_time']


class ServiceProfessionalPostSerializer(serializers.ModelSerializer):

    # def validate_minimum_price(self, value):
    #     service_professional = self.instance
    #     service = service_professional.service
    #     if value < service.minimal_range_price:
    #         raise serializers.ValidationError("O preço mínimo para esse serviço é R${}".format(service.minimal_range_price))

    class Meta:
        model = ServiceProfessional
        fields = ['service', 'minimum_price', 'average_time']


class StateSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):

    class Meta:
        model = City
        fields = '__all__'


class SplitSerializer(serializers.Serializer):
    split_number = serializers.CharField(max_length=200)
    split_price = serializers.CharField(max_length=200)
    split_text = serializers.CharField(max_length=200)
