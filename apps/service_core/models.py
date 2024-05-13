import datetime, random, string, uuid, pytz

from django.db import models, IntegrityError
from django.db.models import Sum, Q
from django.conf import settings
from django.utils import timezone

from model_utils import Choices
from model_utils.fields import MonitorField, StatusField
from simple_history.models import HistoricalRecords

from decimal import Decimal

from apps.common.models import BestPraticesModel, UserAddress
from apps.common.views import Sms
from apps.core.models import Neighborhood
from apps.iugu.invoice import Invoice
from apps.iugu.token import Token
from apps.message_core.models import PushToken
from apps.message_core.views import slack_message
from apps.payment.models import CreditCard, Transaction, Voucher, Payment, PaymentInstallment
from apps.payment.views import calculate_splits, split_payment
from apps.professional.models import Calendar, ProfessionalEvaluation, Schedule, ServiceProfessional, Professional, \
    ServiceProfessionalPricingCriterion, Executive, ProfessionalSchedule

from .views import Notification
# from .tasks import whatsapp_message

# Create your models here.

GENDER_LIST = (
    ('Todos', 'Todos'),
    ('Masculino', 'Masculino'),
    ('Feminino', 'Feminino'),
)

class Category(BestPraticesModel):
    """
    Model for Category object for Services(:model:`service_core.service`)
    """
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=400, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_LIST, default='Todos')
    picture_male = models.ImageField(upload_to='categories/', null=True, blank=True)
    picture_female = models.ImageField(upload_to='categories/', null=True, blank=True)
    icon = models.ImageField(upload_to='categories/icons/', null=True, blank=True)
    history = HistoricalRecords()
    is_demo = models.BooleanField(default=False)
    ordering = models.IntegerField(default=0)

    class Meta:
        verbose_name = "Category"

    def __str__(self):
        return '{}'.format(self.name)


class Service(BestPraticesModel):
    """
    Model for Service object
    """
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    gender = models.CharField(max_length=20, choices=GENDER_LIST, default='Todos')
    mean_range_time = models.PositiveIntegerField(default=0)
    # maximal_range_time = models.PositiveIntegerField(default=0)
    minimal_range_price = models.PositiveIntegerField(default=0)
    # maximal_range_price = models.PositiveIntegerField(default=0)
    pricing_criterion = models.ForeignKey('PricingCriterion', null=True,blank=True)
    picture = models.ImageField(upload_to='services/', null=True, blank=True)
    is_app_enabled = models.BooleanField(default=True)
    can_set_price = models.BooleanField(default=True)
    has_pricing_before = models.BooleanField(default=False)
    default_option = models.ForeignKey('PricingCriterionOptions',null=True, blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Service"

    def __str__(self):
        return '{} - {}'.format(self.name, self.gender)



class Attendance(BestPraticesModel):
    """
    Model for Attendance object
    """
    STATUS = Choices(('draft', 'Rascunho'),
                     ('flexible_draft', 'Rascunho com janela'),
                     ('complete_draft', 'Rascunho Completo'),
                     ('waiting_confirmation', 'Aguardando Confirmação'),
                     ('waiting_payment', 'Aguardando pagamento'),
                     ('waiting_approval', 'Aguardando Confirmação do Cliente'),
                     ('confirmated', 'Confirmado'),
                     ('on_transfer', 'A caminho'),
                     ('waiting_customer', 'Aguardando o Cliente'),
                     ('in_attendance', 'Em atendimento'),
                     ('completed', 'Concluído'),
                     ('canceled', 'Cancelado'),
                     ('canceled_by_customer', 'Cancelado pelo Cliente'),
                     ('canceled_by_professional', 'Cancelado pelo Profissional'),
                     ('expired', 'Expirado'),
                     ('pending_payment', 'Problema no pagamento'),
                     ('scheduling_shock', 'Choque de horário'),
                     ('rejected', 'Rejeitado'))
    professional = models.ForeignKey('professional.Professional', null=True, blank=True)
    customer = models.ForeignKey('customer.Customer', null=True)
    status = StatusField(choices_name='STATUS', default=STATUS.draft, db_index=True, verbose_name='Status')
    scheduling_date = models.DateTimeField(null=True)
    total_duration = models.PositiveIntegerField(default=0, null=True)
    address = models.ForeignKey(UserAddress, null=True, blank=True)
    neighborhood = models.ForeignKey(Neighborhood, null=True, blank=True)
    services = models.ManyToManyField(Service,through='AttendanceService', through_fields=('attendance','service'))
    initial_service = models.ForeignKey(Service, related_name='initial_service', null=True, blank=True)
    credit_card = models.ForeignKey('payment.CreditCard', null=True, blank=True, verbose_name='Cartão de Crédito')
    payment_form = models.ForeignKey('payment.PaymentForm', null=True, blank=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, blank=True, default=0)
    splits_number = models.PositiveIntegerField(blank=True, default=1)
    total_discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_interest = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_administrate_tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    waiting_confirmation_date = MonitorField(monitor='status', when=['waiting_confirmation'], null=True,blank=True, default=None)
    on_transfer_date = MonitorField(monitor='status', when=['on_transfer'], null=True,blank=True, default=None)
    waiting_customer_date = MonitorField(monitor='status', when=['waiting_customer'], null=True,blank=True, default=None)
    confirmated_date = MonitorField(monitor='status', when=['confirmated'], null=True,blank=True, default=None)
    in_attendance_date = MonitorField(monitor='status', when=['in_attendance'], null=True,blank=True, default=None)
    completed_date = MonitorField(monitor='status', when=['completed'], null=True, blank=True, default=None)
    expired_date = MonitorField(monitor='status', when=['expired'], null=True, blank=True, default=None)
    canceled_date = MonitorField(monitor='status', when=['canceled_by_customer', 'canceled_by_professional'], null=True, blank=True, default=None)
    pay_day = models.DateTimeField(null=True, blank=True)
    expected_date_checkout = models.DateTimeField(null=True, blank=True)
    pricing_criterion_option = models.ForeignKey('PricingCriterionOptions',null=True, blank=True)
    observation = models.TextField(null=True, blank=True)
    observation_internal = models.TextField(null=True, blank=True)
    pixel_id = models.TextField(null=True, blank=True)
    has_evaluation = models.BooleanField(default=False)
    has_evaluation_professional = models.BooleanField(default=False)
    is_push_notificated = models.BooleanField(default=False)
    is_sms_notificated = models.BooleanField(default=False)
    is_test = models.BooleanField(default=True)
    voucher = models.ForeignKey(Voucher, null=True, blank=True, verbose_name='Cupom')
    ## Horário do início do período de atendimento flexível
    flexible_date_start = models.DateTimeField(null=True, blank=True,
        verbose_name="Horário inicial"
    )
    ## Horário do fim do período de atendimento flexível
    flexible_date_end = models.DateTimeField(null=True, blank=True,
        verbose_name="Horário final"
    )
    ## Desconto por atendimento flexível
    flexible_discount = models.FloatField(null=True, blank=True, default=0.0)
    type = models.CharField(max_length=20, default='',
                            choices=(('', 'Não informado'),
                                ('has_preference', 'Agendando Diretamente'),
                                     ('dont_has_preference', 'Peça Já')))
    factor = models.DecimalField(max_digits=3, decimal_places=2, default=1.00)

    def calculate_discount(self):
        if self.voucher:
            voucher = self.voucher
            price = self.attendance_relation.first().return_attendance_totals()['total_price']
            if voucher.discount_type == 'percent':
                return Decimal(price * voucher.discount / 100)
            else:
                return Decimal(voucher.discount_value)
        else:
            return Decimal(0)

    def get_biuri_click_price(self):
        #gets the price for a service when the customer does not have
        #a preference for the profession who provides the service
        if settings.DEBUG:
            click_biuri_prices_id = 20
        else:
            click_biuri_prices_id = 96
        return ServiceProfessional.objects.filter(
            service=self.initial_service,
            professional=click_biuri_prices_id).order_by("minimum_price")

    def valid_hours(self, reference_date):
        #Returns the remaining hours until the flex_date_start
        #or raises an error if an incorrect date was chosen
        valid_hours_start = 7
        valid_hours_end = 20
        now = datetime.datetime.now()

        #validates if the date is between business hours or raises an error
        if (valid_hours_start > reference_date.hour) or (reference_date.hour >= valid_hours_end):
            print("date out of range")
            raise Exception("date out of range")

        if valid_hours_start > now.hour:
            now = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now.hour > valid_hours_end:
            now = now.replace(hour=8, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)

        #validates if the date a future date or raises an error
        if now > reference_date:
            print("reference date error")
            raise Exception("reference date error")

        diff_days = (reference_date.replace(hour=0, minute=0, second=0, microsecond=0) - now.replace(hour=0, minute=0, second=0, microsecond=0))
        print('diff_days: ', diff_days)
        print('ref_date: ', reference_date)
        print('now: ', now)

        if diff_days.days == 0:
            hours = diff_days.total_seconds()/(60*60)

        if diff_days.days >= 1:
            seconds = (now.replace(hour=valid_hours_end, minute=0, second=0, microsecond=0) - now).total_seconds() + \
                        (reference_date - reference_date.replace(hour=valid_hours_start, minute=0, second=0, microsecond=0)).total_seconds()

            hours = seconds/(60*60)

            hours = hours + (diff_days.days -1)*(valid_hours_end - valid_hours_start)

        return hours

    def update_factor(self, flexible_date_start, flexible_date_end):
        #if the time window for a flex attendance's date is less than 2h, 1.05
        #if the flex_date_start is in less than 18h, 1.05
        #if the attendance date is on sunday, 1.05
        
        print('updt factor')
        window = (flexible_date_end - flexible_date_start).total_seconds()

        self.factor = 1.00
        if window <= 2*60*60:
            self.factor = 1.05
        if self.valid_hours(flexible_date_start) < 18:
            self.factor = 1.05
        if flexible_date_start.weekday() == 6:
            self.factor = 1.05
        super(Attendance, self).save()
        print('save updt factor')
        return True
    

    def save(self, *args, **kwargs):
        if self.pk:
            old_attendance = Attendance.objects.get(pk=self.pk)
            change = ChangeStatus.change_status(
                self,atual_status=old_attendance.status,new_status=self.status, attendace=self.pk,
                atual_professional=old_attendance.professional, new_professional=self.professional)
            print("DEBUG change={}".format(str(change)))
            if 'professional' in change:
                self.professional = change['professional']
            if 'status' in change:
                self.status = change['status']
            if 'pay_day' in change:
                self.pay_day = change['pay_day']
            if 'total_price' in change:
                self.total_price = change['total_price']
            if 'duration' in change:
                self.total_duration = change['duration']
                self.expected_date_checkout = self.scheduling_date + datetime.timedelta(minutes=change['duration'])
                if self.professional:
                    self.expected_date_checkout = self.scheduling_date + datetime.timedelta(minutes=change['duration']) + datetime.timedelta(minutes=self.professional.attendance_window)
            if 'expected_date_checkout' in change:
                self.expected_date_checkout = change['expected_date_checkout']

           
                
            if self.type == 'has_preference':
                professional_for_price = self.professional
                if professional_for_price is not None:
                    service_professional = ServiceProfessional.objects.filter(
                        service=self.initial_service, professional=professional_for_price).order_by("minimum_price")
            else:
                service_professional = self.get_biuri_click_price()
            if service_professional.exists():
                service_professional = service_professional.first()
                if self.scheduling_date:
                    self.total_duration = service_professional.average_time
                    self.expected_date_checkout = self.scheduling_date + datetime.timedelta(
                        minutes=service_professional.average_time)
                    if self.professional:
                        self.expected_date_checkout = self.scheduling_date + datetime.timedelta(
                            minutes=service_professional.average_time)
                if self.pricing_criterion_option:
                    service_professional_criterion = ServiceProfessionalPricingCriterion.objects.filter(
                        service_professional=service_professional,
                        pricingcriterionoptions=self.pricing_criterion_option)
                    if service_professional_criterion.exists():
                        service_professional_criterion = service_professional_criterion.first()
                        self.total_price = Decimal(service_professional_criterion.price)*Decimal(self.factor)
                    else:
                        self.total_price = Decimal(service_professional.minimum_price)*Decimal(self.factor)
                else:
                    self.total_price = Decimal(service_professional.minimum_price)*Decimal(self.factor)


            self.total_interest = split_payment(float(self.total_price),self.splits_number)*self.splits_number - float(self.total_price)
            # self.factor = Attendance.objects.get(pk=self.pk).factor
        else:
            professional_for_price = None
            if self.type == 'has_preference' or self.professional:
                professional_for_price = self.professional
                if professional_for_price is not None:
                    service_professional = ServiceProfessional.objects.filter(
                        service=self.initial_service, professional=professional_for_price).order_by("minimum_price")
            else:
                service_professional = self.get_biuri_click_price()
            if service_professional.exists():
                service_professional = service_professional.first()
                if self.scheduling_date:
                    self.total_duration = service_professional.average_time
                    self.expected_date_checkout = self.scheduling_date + datetime.timedelta(
                        minutes=service_professional.average_time)
                    if self.professional:
                        self.expected_date_checkout = self.scheduling_date + datetime.timedelta(
                            minutes=service_professional.average_time)
                if self.pricing_criterion_option:
                    service_professional_criterion = ServiceProfessionalPricingCriterion.objects.filter(
                        service_professional=service_professional,
                        pricingcriterionoptions=self.pricing_criterion_option)
                    if service_professional_criterion.exists():
                        service_professional_criterion = service_professional_criterion.first()
                        self.total_price = Decimal(service_professional_criterion.price)*Decimal(self.factor)
                    else:
                        self.total_price = Decimal(service_professional.minimum_price)*Decimal(self.factor)
                else:
                    self.total_price = Decimal(service_professional.minimum_price)*Decimal(self.factor)


            self.total_interest = split_payment(float(self.total_price),self.splits_number)*self.splits_number - float(self.total_price)
        try:
            #if voucher has been apply, recalculate the value of the discount
            if self.voucher:
                self.total_discount = self.calculate_discount()
        except Exception as e:
            print(e)
        try:
            services = AttendanceService.objects.filter(attendance=self).first()
            totals=services.return_attendance_totals()
            self.total_price = totals['total_price']
            self.total_duration = totals['total_duration']
            self.total_administrate_tax = totals['total_administrate_tax']
            self.total_interest = split_payment(float(self.total_price),self.splits_number)*self.splits_number - float(self.total_price)
        except Exception as e:
            print(e)
        attendance = super(Attendance, self).save(*args, **kwargs)
        if self.status == 'confirmated':
            self.process_calendar(type='confirmated')
        
        return attendance

    class Meta:
        verbose_name = "Attendance"

    def __str__(self):
        return '{}'.format(self.id)

    @property
    def get_total_price(self):
        return round(float(self.total_price) + float(self.total_interest) - float(self.total_discount) ,2)

    def split(self, token):
        attendance = self
        if (token['invoice_id'] is not None):
            invoice = Invoice().search(id=token['invoice_id'])
            payment = Payment.objects.filter(attendance=attendance, invoice_id=token['invoice_id'], status='accepted')
            if payment.exists():
                payment = payment[0]
            else:
                payment = Payment(attendance=attendance, invoice_id=token['invoice_id'], information_data=invoice, status='accepted', amount=attendance.get_total_price)
                payment.save()
            installments_model = []
            try:
                installments = invoice['financial_return_dates']
                #if there are installments (antecipação), check that they have been registered as PaymentInstallments, otherwise register them
                for installment in installments:
                    p = PaymentInstallment.objects.filter(payment=payment, installment_id=installment['id'])
                    if not p.exists():
                        installment_model = PaymentInstallment(payment=payment,
                                                               installment_id=installment['id'],
                                                               installment_data=installment)
                        installments_model.append(installment_model)
                #bulk_create to register the installments in django's db
                PaymentInstallment.objects.bulk_create(installments_model)
            #if there are no installments, pass
            except Exception:
                pass
            paid_cents = invoice['paid_cents']
            taxes_paid_cents = invoice['taxes_paid_cents']
        else:
            paid_cents = int(attendance.total_price * 100) - int(attendance.total_discount * 100)
            taxes_paid_cents = 0
        paid_cents = paid_cents - int(attendance.total_interest * 100)
        if attendance.voucher:
            if attendance.voucher.type == 'marketplace':
                transaction_discount = Transaction(attendance=attendance, price=(attendance.total_discount * -1),
                                                   type='discount')
                transaction_discount.save()
                paid_cents += int(attendance.total_discount * 100)
        taxa_marketplace = int(paid_cents * 0.15)
        professional_percent = float(attendance.professional.attendance_percent / 100)
        taxa_profissional = int(paid_cents * professional_percent)
        taxa_executivo = paid_cents - taxa_profissional - taxa_marketplace
        taxa_marketplace -= taxes_paid_cents

        transaction_professional = Transaction(attendance=attendance, price=taxa_profissional / 100,
                                               type='professional')
        transaction_professional.save()

        transaction_executivo = Transaction(attendance=attendance, price=taxa_executivo / 100,
                                            type='executive')
        transaction_executivo.save()

        transaction_marketplace = Transaction(attendance=attendance, price=taxa_marketplace / 100,
                                              type='marketplace')
        transaction_marketplace.save()

        transaction_taxes = Transaction(attendance=attendance, price=taxes_paid_cents / 100, type='tax',
                                        is_recebido=True)
        transaction_taxes.save()

        if attendance.total_interest > 0:
            transaction_tax_interest = Transaction(attendance=attendance, price=attendance.total_interest,
                                                   type='tax_interest', is_recebido=True)
            transaction_tax_interest.save()

    def refund(self):
        payments = Payment.objects.filter(attendance=self, status='accepted')
        for payment in payments:
            invoice = Invoice()
            invoice.refund(payment.invoice_id)
            payment.status = 'refunded'
            payment.save()

    def charge(self, total=None):
        attendance = self
        if (attendance.total_price - attendance.total_discount) <= 0:
            return {'success': True, "invoice_id": None}
        payment = Payment.objects.filter(attendance=attendance, status='accepted')
        if payment.exists():
            payment = payment[0]
            if payment.amount == attendance.get_total_price:
                return payment.information_data
            attendance.refund()
        items = []
        services = AttendanceService.objects.filter(attendance=attendance)
        for service in services:
            items.append({'description': service.service.name, 'quantity': service.quantity,
                          'price_cents': int(Decimal(service.price_cents())*Decimal(self.factor))})
        if len(items) == 0:
            items.append({'description': attendance.initial_service.name, 'quantity': 1,
                          'price_cents': total if total is not None else int(attendance.total_price * 100)})
        
        if attendance.total_interest > 0:
            items.append({'description': "Juros Parcelamento", 'quantity': 1,
                          'price_cents': int(attendance.total_interest * 100)})
        discount = int(attendance.total_discount * 100)
        #if production settings, and test attendance/credit card, skip
        #if (not settings.DEBUG) and (attendance.is_test):
        #    return {}
        token_card = Token().create(dict(attendance.credit_card.card_data))['id']
        data = {
            'token': token_card,
            'customer_id': attendance.customer.iugu_client_id,
            'email': attendance.customer.user.email,
            'items': items,
            'discount_cents': discount,
            'months': attendance.splits_number,
            'test': True
        }
        token = Token().charge(data)
        status = 'rejected'
        if 'success' in token:
            if token['success']:
                status = 'accepted'
        payment = Payment(attendance=attendance, invoice_id=token['invoice_id'], information_data=token,
                            status=status, amount=attendance.get_total_price)
        payment.save()
        return token


    def process_calendar(self, type):
        attendance = self
        if attendance.professional:
            schedule_attendance_delete = Schedule.objects.filter(attendance=attendance).delete()
            if type=='confirmated':
                checkout_date = attendance.scheduling_date + datetime.timedelta(minutes=attendance.total_duration)
                schedule_attendance = Schedule(professional=attendance.professional,
                                               daily_date=attendance.scheduling_date.date(),
                                               attendance=attendance,
                                               daily_time_begin=(datetime.datetime.combine(attendance.scheduling_date.date(),
                                                                                           attendance.scheduling_date.time()) - datetime.timedelta(
                                                   minutes=attendance.professional.attendance_window)).time(),
                                               daily_time_end=(datetime.datetime.combine(checkout_date.date(),
                                                                                           checkout_date.time()) + datetime.timedelta(
                                                   minutes=attendance.professional.attendance_window)).time())
                professional_schedule = Schedule.objects.filter(professional=attendance.professional,
                                                                daily_date=attendance.scheduling_date.date(),
                                                                daily_time_begin__lte=attendance.scheduling_date.time(),
                                                                daily_time_end__gte=checkout_date.time())
                if professional_schedule.exists():
                    professional_schedule = professional_schedule[0]
                    datetime_begin_window_date = datetime.datetime.combine(attendance.scheduling_date.date(),
                                                                           attendance.scheduling_date.time()) - datetime.timedelta(
                        minutes=attendance.professional.attendance_window)
                    professional_schedule_begin_date = datetime.datetime.combine(professional_schedule.daily_date,
                                                                                 professional_schedule.daily_time_begin)
                    if professional_schedule_begin_date > datetime_begin_window_date:
                        schedule_attendance.daily_time_begin = professional_schedule.daily_time_begin
                schedule_attendance.save()
                if attendance.professional.is_saloon:
                    pass
                else:
                    attendances_conflict_calendar = Attendance.objects.filter(professional=attendance.professional,
                                                                            scheduling_date__date=attendance.scheduling_date.date(),
                                                                            status='waiting_confirmation') \
                        .filter(Q(scheduling_date__time__gte=attendance.scheduling_date.time(),
                                scheduling_date__time__lte=checkout_date.time()) |
                                Q(expected_date_checkout__time__gte=attendance.scheduling_date.time(),
                                expected_date_checkout__time__lte=checkout_date.time()) |
                                Q(scheduling_date__time__lte=attendance.scheduling_date.time(),
                                expected_date_checkout__time__gte=checkout_date.time()))
                    for attendances_conflict in attendances_conflict_calendar:
                        if attendances_conflict.pk != attendance.pk:
                            attendances_conflict.status = 'scheduling_shock'
                            attendances_conflict.save()
            calendar = Calendar()
            calendar.process_full_calendar(attendance.professional.pk, attendance.scheduling_date.date())

    @property
    def evaluation_comment(self):
        evaluation = ProfessionalEvaluation.objects.filter(attendance=self, description__isnull=False)
        if evaluation.exists():
            return evaluation[0].description
        return ''

    @property
    def split_payments(self):
        return calculate_splits(price=float(self.total_price) - float(self.total_discount),minimal_split_price=40)


class AttendanceProfessionalConfirmation(BestPraticesModel):
    """
    Allows the Professional(:model:`professional.professional`) to accept an Attendance(:model:`service_core.attendance`) from Click Biuri
    """
    attendance = models.ForeignKey(Attendance)
    professional = models.ForeignKey('professional.Professional')
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return '{}'.format(self.id)


class AttendanceService(BestPraticesModel):
    """
    Stores the Services(:model:`serivce_core.service`) for a single Attendance(:model:`service_core.attendance`)
    """
    service = models.ForeignKey(Service, verbose_name='Serviço')
    attendance = models.ForeignKey(Attendance, related_name="attendance_relation", related_query_name='attendance_relation')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Preço')
    duration = models.IntegerField(verbose_name='Duração (Minutos)')
    is_in_attendance = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1, verbose_name='Quantidade')

    class Meta:
        verbose_name = "Attendance Service"

    def __str__(self):
        return '{}-{}'.format(self.service, self.attendance)

    def save(self, *args, **kwargs):
        attendanceservice = super(AttendanceService, self).save(*args, **kwargs)
        self.update_attendace()
        return attendanceservice

    def delete(self, *args, **kwargs):
        attendanceservice = super(AttendanceService, self).delete(*args, **kwargs)
        self.update_attendace()
        return attendanceservice

    def update_attendace(self):
        attendance = self.attendance
        attendance_services = AttendanceService.objects.filter(attendance=attendance)
        if attendance_services.exists():
            attendance.total_price = attendance_services.aggregate(y=Sum('price'))['y']
            duration = attendance_services.aggregate(y=Sum('duration'))['y']
            attendance.total_duration = duration
            if attendance.scheduling_date:
                if attendance.professional:
                    attendance.expected_date_checkout = attendance.scheduling_date \
                                                        + datetime.timedelta(minutes=duration)
                else:
                    attendance.expected_date_checkout = attendance.scheduling_date + datetime.timedelta(minutes=duration)
        else:
            attendance.total_price = 0
            attendance.total_duration = 0
            attendance.total_administrate_tax = 0
        try:
            if attendance.voucher:
                attendance.total_discount=attendance.calculate_discount()
        except Exception as e:
            print(e)
        attendance.save()

    def return_attendance_totals(self):
        attendance = self.attendance
        attendance_services = AttendanceService.objects.filter(attendance=attendance)
        if attendance_services.exists():
            attendance.total_price = attendance_services.aggregate(y=Sum('price'))['y']
            duration = attendance_services.aggregate(y=Sum('duration'))['y']
            attendance.total_duration = duration
            if attendance.scheduling_date:
                if attendance.professional:
                    attendance.expected_date_checkout = attendance.scheduling_date \
                                                        + datetime.timedelta(minutes=duration)
                else:
                    attendance.expected_date_checkout = attendance.scheduling_date + datetime.timedelta(minutes=duration)
        else:
            attendance.total_price = 0
            attendance.total_duration = 0
            attendance.total_administrate_tax = 0
        attendance_totals = {
            'total_price': Decimal(attendance.total_price)*Decimal(attendance.factor),
            'total_duration': attendance.total_duration,
            'total_administrate_tax': attendance.total_administrate_tax
        }
        return attendance_totals

    def price_cents(self):
        return int(self.price * 100)



class ChangeStatus():
    def get_biuri_click_price_on_status_change(attendance):
        #gets the price for a service when the customer does not have
        #a preference for the profession who provides the service
        if settings.DEBUG:
            click_biuri_prices_id = 20
        else:
            click_biuri_prices_id = 96
        print(ServiceProfessional.objects.filter(
                service=attendance.initial_service,
                professional=click_biuri_prices_id).order_by("minimum_price"))
        return ServiceProfessional.objects.filter(
                service=attendance.initial_service,
                professional=click_biuri_prices_id).order_by("minimum_price")

    def change_status(self, atual_status,new_status,attendace, atual_professional,
        new_professional):
        print('CHANGE STATUS')
        response = {}
        response['atual_status'] = atual_status
        response['new_status'] = new_status
        attendance = Attendance.objects.select_related('professional__user','initial_service','customer__user').get(pk=attendace)
        attendance_dict = {'id': attendance.id, 'status': new_status}
        professional_tokens = PushToken.objects.none()
        customer_tokens = PushToken.objects.none()
        slack_message_text = 'Novo atendimento número {}'.format(attendance.pk)
        if attendance.professional:
            professional_tokens = PushToken.objects.filter(user=attendance.professional.user)
            slack_message_text += ' para {}'.format(attendance.professional.user.first_name)
        if attendance.customer:
            customer_tokens = PushToken.objects.filter(user=attendance.customer.user)
            slack_message_text += ' criado por {}'.format(attendance.customer.user.first_name)
        notification = Notification()


        #update the factor if status changes to flex_draft, or is already flex_draft and change the dates

        if atual_status in ('draft', 'complete_draft', 'flexible_draft') and new_status=='waiting_confirmation':
            if professional_tokens.exists():
                checkout = attendance.scheduling_date + datetime.timedelta(minutes=attendance.initial_service.mean_range_time)
                print(checkout)
            else:
                checkout = attendance.scheduling_date
                print(checkout)
            response['expected_date_checkout'] = checkout
            if attendance.scheduling_date:
                slack_message_text += ' para ' + str(attendance.scheduling_date)
            url = 'http://www.biuri.com.br/after_sale/attendance/{}/edit'.format(attendance.pk)
            # slack_message(slack_message_text + ' ' + url)
            services_attendance = AttendanceService.objects.filter(attendance=attendance)
            if not services_attendance:
                attendanceservice = AttendanceService(attendance=attendance, service=attendance.initial_service)
                if attendance.type == 'has_preference':
                    professional_service = ServiceProfessional.objects.filter(service=attendance.initial_service,
                                                                        professional=attendance.professional).order_by("minimum_price")
                    if not attendance.pricing_criterion_option:
                        attendanceservice.price = professional_service[0].minimum_price
                    else:
                        professional_pricing_criterion = ServiceProfessionalPricingCriterion.objects.filter(
                            service_professional=professional_service[0],
                            pricingcriterionoptions=attendance.pricing_criterion_option)
                        if professional_pricing_criterion.exists():
                            attendanceservice.price = professional_pricing_criterion[0].price
                        else:
                            attendanceservice.price = professional_service[0].minimum_price
                else:
                    professional_service = ChangeStatus.get_biuri_click_price_on_status_change(attendance=attendance)
                    if not attendance.pricing_criterion_option:
                        attendanceservice.price = professional_service[0].minimum_price
                    else:
                        professional_pricing_criterion = ServiceProfessionalPricingCriterion.objects.filter(
                            service_professional=professional_service[0],
                            pricingcriterionoptions=attendance.pricing_criterion_option)
                        if professional_pricing_criterion.exists():
                            attendanceservice.price = professional_pricing_criterion[0].price
                        else:
                            attendanceservice.price = professional_service[0].minimum_price
                attendanceservice.duration = professional_service[0].average_time
                attendanceservice.save()
                response['total_price'] = attendanceservice.price
                response['duration'] = attendanceservice.duration
                if professional_tokens.exists():
                    checkout = attendance.scheduling_date + datetime.timedelta(minutes=attendance.initial_service.mean_range_time)
                    print(checkout)
                    response['expected_date_checkout'] = attendance.scheduling_date + datetime.timedelta(minutes=attendanceservice.duration)
                else:
                    checkout = attendance.scheduling_date
                    print(checkout)
                    response['expected_date_checkout'] = attendance.scheduling_date
            if attendance.type == 'has_preference':
                if professional_tokens:
                    for professional_token in professional_tokens:
                        try:
                            notification.push(
                                data=attendance_dict,
                                to=professional_token.token,
                                title='Biuri',
                                body='Novo Serviço disponível'
                            )
                        except Exception as e:
                            print(e)
                msg = 'Você recebeu um novo atendimento. Em caso de duvidas, ligue para: (81)991548306'
                #if it fails to find the executive cellphone, it will use the default msg instead
                try:
                    msg = 'Você recebeu um novo atendimento. Em caso de duvidas, ligue para: {}'.format(attendance.professional.executive.cellphone)
                except Exception:
                    pass
                try:
                    data = {'to': str(55) + attendance.professional.celphone, 'from': 'BIURI',
                        'msg': msg}
                    sms = Sms()
                    sms.send(data=data)
                #if it fails to deliver an SMS to the professional, it will send a notification
                except Exception:
                    professional_tokens = PushToken.objects.filter(user=attendance.professional.user)
                    if professional_tokens:
                        notification.push(
                            data=attendance_dict,
                            to=professional_token[0].token,
                            title='Você recebeu um novo atendimento',
                            body=msg
                        )
                    else:
                        pass
            else:
                professionals = Professional.objects.select_related('user').filter(categorys__services=attendance.initial_service,
                                                                   citys__city__name=attendance.address.city.upper(),
                                                                    professional_enabled=True,
                                                                    professional_enabled_executive=True)
                # response['total_price'] = 0
                # response['duration'] = attendance.initial_service.mean_range_time
                for professional in professionals:
                    professional_attendance = AttendanceProfessionalConfirmation(professional=professional, attendance=attendance)
                    professional_attendance.save()
                    professional_tokens = PushToken.objects.filter(user=professional.user)
                    if professional_tokens:
                        for professional_token in professional_tokens:
                            notification.push(
                                data=attendance_dict,
                                to=professional_token.token,
                                title='Biuri',
                                body='Novo Serviço disponível'
                            )

        if (atual_status=='waiting_confirmation' and new_status=='confirmated'):
            # schedule = Schedule.objects.filter(professional=attendance.professional).filter(daily_date=attendance.scheduling_date.astimezone().date(),daily_time_begin__lte=attendance.scheduling_date.astimezone().time(),daily_time_end__gte=attendance.expected_date_checkout.astimezone().time())
            # Mandar notificação pro cliente da confirmação e alocar na agenda do profissional
            if not attendance.services.exists():
                attendanceservice = AttendanceService(attendance=attendance, service=attendance.initial_service)
                professional_service = ServiceProfessional.objects.get(service=attendance.initial_service,
                                                                       professional=attendance.professional)
                if not attendance.pricing_criterion_option:
                    attendanceservice.price = professional_service.minimum_price
                else:
                    professional_pricing_criterion = ServiceProfessionalPricingCriterion.objects.get(
                        service_professional=professional_service, pricingcriterionoptions=attendance.pricing_criterion_option)
                    attendanceservice.price = professional_pricing_criterion.price
                attendanceservice.duration = professional_service.average_time
                attendanceservice.save()
                response['total_price'] = attendanceservice.price
                response['duration'] = attendanceservice.duration
                response['expected_date_checkout'] = attendance.scheduling_date + datetime.timedelta(
                    minutes=attendanceservice.duration)

            if customer_tokens:
                for customer_token in customer_tokens:
                    push_text = 'Atendimento aceito por ' + attendance.professional.user.first_name
                    notification.push(
                        data=attendance_dict,
                        to=customer_token.token,
                        title='Biuri',
                        body=push_text
                    )

        if (atual_status=='waiting_confirmation' and new_status=='rejected'):
            # Mandar notificação pro cliente que o profissional está a caminho
            attendance.process_calendar(type=new_status)
            attendance.refund()
            if customer_tokens:
                for customer_token in customer_tokens:
                    push_text = 'O profissional está indisponível para atendimento'
                    notification.push(
                        data=attendance_dict,
                        to=customer_token.token,
                        title='Biuri',
                        body=push_text
                    )

        
        if (new_status=='canceled'):
            # Cancel notification, clear calendar and refund
                attendance.process_calendar(type=new_status)
                attendance.refund()

        if (atual_status=='waiting_confirmation' and new_status=='scheduling_shock'):
            # Mandar notificação pro cliente que o profissional está a caminho
            attendance.refund()
            if customer_tokens:
                for customer_token in customer_tokens:
                    push_text = 'O profissional está indisponível para atendimento'
                    notification.push(
                        data=attendance_dict,
                        to=customer_token.token,
                        title='Biuri',
                        body=push_text
                    )

        if (atual_status=='confirmated' and new_status=='on_transfer'):
            # Mandar notificação pro cliente que o profissional está a caminho
            if customer_tokens:
                for customer_token in customer_tokens:
                    push_text = attendance.professional.user.first_name + ' está a caminho do atendimento'
                    notification.push(
                        data=attendance_dict,
                        to=customer_token.token,
                        title='Biuri',
                        body=push_text
                    )

        if (new_status=='canceled_by_professional'):
            # Mandar notificação pro cliente que o profissional cancelou o atendimento
            attendance.process_calendar(type=new_status)
            attendance.refund()
            if customer_tokens:
                for customer_token in customer_tokens:
                    push_text = attendance.professional.user.first_name + ' cancelou o atendimento'
                    notification.push(
                        data=attendance_dict,
                        to=customer_token.token,
                        title='Biuri',
                        body=push_text
                    )

        if (new_status=='canceled_by_customer'):
            # Mandar notificação pro profissional que o cliente cancelou o atendimento
            attendance.process_calendar(type=new_status)
            attendance.refund()
            if professional_tokens:
                for professional_token in professional_tokens:
                    push_text = attendance.customer.user.first_name + ' cancelou o atendimento'
                    notification.push(
                        data=attendance_dict,
                        to=professional_token.token,
                        title='Biuri',
                        body=push_text
                    )

        if (atual_status=='canceled_by_customer' and new_status=='confirmated'):
            response['status'] = 'canceled_by_customer'

        if ((atual_status=='on_transfer' or atual_status=='confirmated') and (new_status=='waiting_customer')):
            # Mandar notificação pro cliente que o profissional chegou
            if customer_tokens:
                for customer_token in customer_tokens:
                    push_text = attendance.professional.user.first_name + ' chegou ao local do atendimento'
                    notification.push(
                        data=attendance_dict,
                        to=customer_token.token,
                        title='Biuri',
                        body=push_text
                    )

        if ((atual_status=='on_transfer' or atual_status=='confirmated' or atual_status=='waiting_customer') and (new_status=='in_attendance')):
            # Mandar notificação pro cliente que o profissional chegou
            if customer_tokens:
                for customer_token in customer_tokens:
                    push_text = attendance.professional.user.first_name + ' iniciou o atendimento'
                    notification.push(
                        data=attendance_dict,
                        to=customer_token.token,
                        title='Biuri',
                        body=push_text
                    )

        if (new_status=='expired'):
            attendance.refund()
            print('Atendimento expirado')
            # Mandar notificação pro cliente que o atendimento expirou
            if customer_tokens:
                for customer_token in customer_tokens:
                    if attendance.professional:
                        push_text = 'O profissional está indisponível para atendimento'
                        notification.push(
                            data=attendance_dict,
                            to=customer_token.token,
                            title='Biuri',
                            body=push_text
                        )
                    else:
                        push_text = 'Não foram encontrados profissionais para a solicitação'
                        notification.push(
                            data=attendance_dict,
                            to=customer_token.token,
                            title='Biuri',
                            body=push_text
                        )

        if (new_status=='canceled_by_customer'):
            attendance.process_calendar(type=new_status)
            attendance.refund()

        if (new_status == 'confirmated'):
            response['expected_date_checkout'] = attendance.scheduling_date + datetime.timedelta(
                minutes=attendance.total_duration)
            attendance.process_calendar(type=new_status)

        if new_professional != atual_professional:
            attendance.process_calendar(type='new_status')
            response['professional'] = new_professional

        if (atual_status=='in_attendance' and new_status=='completed'):
            print('Atendimento Finalizado')
            token = attendance.charge()
            if not 'success' in token:
                response['status'] = 'pending_payment'
                if customer_tokens:
                    push_text = 'Ocorreu um problema com o pagamento'
                    for customer_token in customer_tokens:
                        notification.push(
                            data=attendance_dict,
                            to=customer_token.token,
                            title='Biuri',
                            body=push_text
                        )
                if professional_tokens:
                    push_text = 'Ocorreu um problema com o pagamento'
                    for professional_token in professional_tokens:
                        notification.push(
                            data=attendance_dict,
                            to=professional_token.token,
                            title='Biuri',
                            body=push_text
                        )
            else:
                if token['success'] == True:
                    response['pay_day'] = datetime.datetime.now()
                    attendance.split(token=token)
                    if customer_tokens:
                        for customer_token in customer_tokens:
                            push_text = 'Obrigado por utilizar a Biuri'
                            notification.push(
                                data=attendance_dict,
                                to=customer_token.token,
                                title='Biuri',
                                body=push_text
                            )
                    if professional_tokens:
                        for professional_token in professional_tokens:
                            notification.push(
                                data=attendance_dict,
                                to=professional_token.token,
                                title='Biuri',
                                body='Pagamento efetuado com sucesso'
                            )
                else:
                    response['status'] = 'pending_payment'
                    if customer_tokens:
                        push_text = 'Ocorreu um problema com o pagamento'
                        for customer_token in customer_tokens:
                            notification.push(
                                data=attendance_dict,
                                to=customer_token.token,
                                title='Biuri',
                                body=push_text
                            )
                    if professional_tokens:
                        push_text = 'Ocorreu um problema com o pagamento'
                        for professional_token in professional_tokens:
                            notification.push(
                                data=attendance_dict,
                                to=professional_token.token,
                                title='Biuri',
                                body=push_text
                            )
        return response


class PricingCriterion(BestPraticesModel):
    """
    Model for Pricing Criterion
    """
    description = models.CharField(max_length=200)
    picture_male = models.ImageField(upload_to='pricingcriterions/', null=True, blank=True)
    picture_female = models.ImageField(upload_to='pricingcriterions/', null=True, blank=True)

    class Meta:
        verbose_name = "Pricing Criterion"

    def __str__(self):
        return '{}'.format(self.description)

    @property
    def get_options(self):
        return PricingCriterionOptions.objects.filter(pricing_criterion=self)


class PricingCriterionOptions(BestPraticesModel):
    """
    Model for the Options for a single Pricing Criterion(:model:`service_core.PricingCriterion`)
    """
    pricing_criterion = models.ForeignKey(PricingCriterion, related_name='options')
    description = models.CharField(max_length=200)

    class Meta:
        verbose_name = "Pricing Criterion Option"

    def __str__(self):
        return '{}'.format(self.description)


class CancelationReason(BestPraticesModel):
    """
    Model for Cancellation Reasons
    """
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=[('customer','customer'), ('professional','professional')])
    is_rejection = models.BooleanField(default=False)
    need_obs = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.name)


class AttendanceCancelation(BestPraticesModel):
    """
    Stores the Cancellation Reason(:model:`service_core.CancelationReason`) for an Attendance(:model:`service_core.attendance`)
    """
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)
    type = models.CharField(max_length=20, choices=[('customer','customer'), ('professional','professional')])
    is_rejection = models.BooleanField(default=False)
    cancelation_reason = models.ForeignKey(CancelationReason)
    obs = models.CharField(max_length=1000, null=True, blank=True)

    def __str__(self):
        return "{}".format(self.id)
