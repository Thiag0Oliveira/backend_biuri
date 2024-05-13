from datetime import time
import unidecode

from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import Group

import requests
from allauth.socialaccount.models import SocialAccount, SocialToken

from apps.common.scrapper import get_user_information
from apps.common.views import Sms, generator_code, PermissionCreateView, PermissionListView, PermissionUpdateView
from apps.common.models import BestPraticesModel
from apps.core.models import City, Neighborhood
from apps.customer.models import Customer
from apps.iugu.models import IuguMarketplaceAccount
from apps.omie.clientes import Cliente

from . import calendar


GENDER_LIST = (
    ('Masculino', 'Masculino'),
    ('Feminino', 'Feminino'),
)

GENDER_LIST_ATTENDANCE = (
    ('all', 'Homem e Mulher'),
    ('male', 'Apenas Homem'),
    ('female', 'Apenas Mulher'),
)

GENDER_ATTENDANCE = {
    'all': 'Homem e Mulher',
    'male': 'Apenas Homem',
    'female': 'Apenas Mulher',
}

DAYS_OF_WEEK = [
        ('0', 'SEGUNDA-FEIRA'),
        ('1', 'TERÇA-FEIRA'),
        ('2', 'QUARTA-FEIRA'),
        ('3', 'QUINTA-FEIRA'),
        ('4', 'SEXTA-FEIRA'),
        ('5', 'SÁBADO'),
        ('6', 'DOMINGO'),
    ]

PAYMENT_FREQUENCY_LIST = [
    ('7', 'SEMANAL'),
    ('15', 'QUINZENAL'),
    ('30', 'MENSAL')
]

PROFESSIONAL_STATUS = (
    ('-', '-'),
    ('Cadastro completo', 'Cadastro completo'),
    ('Ativado', 'Ativado'),
    ('Aprovado no Teste', 'Aprovado no Teste'),
    ('Reprovado no Teste', 'Reprovado no Teste'),
    ('Desvinculado', 'Desvinculado'),
    ('Sem interesse', 'Sem interesse'),
)


class Professional(BestPraticesModel, IuguMarketplaceAccount):
    """
    Model for Professional object
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    description = models.TextField(max_length=500, null=True, blank=True, verbose_name='Descrição do profissional')
    observation = models.TextField(max_length=500, null=True, blank=True, verbose_name='Observações sobre profissional')
    avatar = models.ImageField(upload_to='professional/avatar/', default='professional/avatar/default.png', blank=True)
    badges = models.ManyToManyField('Badge', through='ProfessionalBadge', through_fields=['professional','badge'], related_name='badges_related')
    attendance_completed_count = models.PositiveIntegerField(default=0)
    attendance_cancelation_count = models.PositiveIntegerField(default=0)
    rating = models.PositiveIntegerField(default=5, verbose_name='Rating')
    category = models.ForeignKey('service_core.Category', verbose_name='Área Principal', related_name='professional_principal')
    evaluations = models.ManyToManyField('service_core.Attendance', through='ProfessionalEvaluation', through_fields=['professional','attendance'], related_name='evaluation_related')
    professional_verified = models.BooleanField(default=False)
    professional_enabled = models.BooleanField(default=False, verbose_name="Profissional Liberado")
    status = models.CharField(max_length=20, choices=PROFESSIONAL_STATUS, default='-', verbose_name='Status')
    professional_enabled_executive = models.BooleanField(default=True, verbose_name="Profissional Liberado pelo Executivo")
    executive = models.ForeignKey('Executive', null=True, blank=True, verbose_name="Executivo")
    celphone = models.CharField(max_length=11, null=True, blank=True, verbose_name='Telefone')
    birthday = models.DateField(null=True, blank=True, verbose_name='Aniversário')
    gender = models.CharField(max_length=20, choices=GENDER_LIST, null=True, blank=True, verbose_name='Sexo')
    gender_attendance = models.CharField(max_length=20, choices=GENDER_LIST_ATTENDANCE, default='all' , verbose_name='Sexos para atendimento')
    categorias = models.ManyToManyField('service_core.Category', through='ProfessionalCategory', through_fields=['professional','category'])
    cidades = models.ManyToManyField(City, through='ProfessionalCity', through_fields=['professional','city'])
    send_sms = models.BooleanField(default=False)
    instagram_username = models.CharField(max_length=30, null=True, blank=True)
    attendance_percent = models.PositiveIntegerField(default=70, validators=[MaxValueValidator(85), MinValueValidator(60)], verbose_name="Percentual do Profissional")
    attendance_window = models.PositiveIntegerField(default=90, validators=[MaxValueValidator(120), MinValueValidator(20)], verbose_name="Janela de tempo entre atendimentos")
    search_text = models.CharField(db_index=True, max_length=200, default='')
    payment_frequency = models.CharField(max_length=20, choices=PAYMENT_FREQUENCY_LIST, default='7', verbose_name='Dias de recebimento')
    full_name = models.CharField(max_length=200, verbose_name='Nome Completo/Razão Social', default='')
    is_test = models.BooleanField(default=False, verbose_name="Profissional de Teste")
    is_saloon = models.BooleanField(default=False, verbose_name="Empresas/salões")

    class Meta:
        verbose_name = "Professional"
        permissions = (('can_liberate_professional','Poder liberar um profissional para receber atendimentos'),
                       ('can_edit_executive','Pode editar o executivo relacionado ao profissional'),
                       ('list_professional', 'Pode ver a Lista de Profissionais'))

    def __str__(self):
        return '{} - {}'.format(self.user.username, self.full_name)

    def save(self, *args, **kwargs):
        self.search_text = '{} {}'.format(unidecode.unidecode(self.user.first_name), unidecode.unidecode(self.user.last_name))
        # data = {
        #     "codigo_cliente_integracao": self.user.username,
        #     "email": self.user.email,
        #     "razao_social": self.user.get_full_name(),
        #     "nome_fantasia": self.user.get_full_name(),
        #     "cnpj_cpf": self.user.username,
        #     "endereco": self.address.address,
        #     "endereco_numero": self.address.number,
        #     "bairro": self.address.neighborhood,
        #     "complemento": self.address.complemento,
        #     "cidade": "{} ({})".format(self.address.city.upper(),self.address.state.upper()),
        #     "estado": self.address.state.upper(),
        #     "cep": self.address.postal_code
        # }
        # c = Cliente()
        # cliente_omie = c.create(data=data)
        # # if not self.iugu_account_data:
        # #     account = MarketPlace().create()
        # #     print(account)
        # #     self.iugu_account_data = account
        return super(Professional, self).save(*args, **kwargs)

    @property
    def get_instagram_pictures(self):
        username = self.instagram_username
        images_list = {}
        try:
            if ( username and username != '' ):
                username = username.replace('@','')
                images = get_user_information(username)['edge_owner_to_timeline_media']['edges']
                if len(images) > 0:
                    images_list['images'] = []
                    for image in images:
                        # if '#biuriapp' in image['node']['edge_media_to_caption']['edges'][0]['node']['text']:
                        #     images_list['images'].append({'thumbnail' : {'url': image['node']['thumbnail_resources'][0]['src']}, 'standard_resolution': {'url': image['node']['thumbnail_resources'][-1]['src']}})
                        images_list['images'].append(
                            {'thumbnail': {'url': image['node']['thumbnail_resources'][0]['src']},
                             'standard_resolution': {'url': image['node']['thumbnail_resources'][-1]['src']}})
            else:
                pictures = ProfessionalPicture.objects.filter(professional_id=self.pk)
                if pictures.exists():
                    images_list['images'] = []
                    for picture in pictures:
                        images_list['images'].append(
                            {'thumbnail': {'url': 'http://www.biuri.com.br' + picture.picture.url},
                             'standard_resolution': {'url': 'http://www.biuri.com.br' + picture.picture.url}})
            return images_list
        except:
            return images_list

    @property
    def get_evaluations(self):
        evaluations = ProfessionalEvaluation.objects.filter(professional__pk=self.pk, description__isnull=False, evaluation_type__isnull=True).exclude(description='').order_by('-created').values('id','description')
        return evaluations[:4]

    @property
    def get_citys(self):
        citys = ProfessionalCity.objects.filter(professional__pk=self.pk)
        return citys

    @property
    def get_services(self):
        services = ServiceProfessional.objects.filter(professional__pk=self.pk)
        return services

    def update_attendance_completed_count(self):
        self.attendance_completed_count = self.attendance_set.filter(status='completed').count()
        self.attendance_cancelation_count = self.attendance_set.filter(status='canceled_by_professional').count()
        self.save()
        return 'success'


class ProfessionalCity(models.Model):
    """
    Stores the Cities(:model:`core.city`) for a single Professional(:model:`professional.professional`)
    """
    professional = models.ForeignKey(Professional, on_delete=models.DO_NOTHING, related_name='citys')
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, verbose_name='Cidade')
    neighborhoods = models.ManyToManyField(Neighborhood, verbose_name='Bairros')

    def __str__(self):
        return '{}'.format(self.id)


class ProfessionalCategory(models.Model):
    """
    Stores the Categories(:model:`service_core.category`) for a single Professional(:model:`professional.professional`)
    """
    professional = models.ForeignKey(Professional, on_delete=models.DO_NOTHING, related_name='categorys')
    category = models.ForeignKey('service_core.Category', on_delete=models.DO_NOTHING, verbose_name='Categoria')
    services = models.ManyToManyField('service_core.Service', verbose_name='Serviços')

    def __str__(self):
        return '{}'.format(self.id)


class ProfessionalCriterion(models.Model):
    """
    Stores the Pricing Criterions(:model:`service_core.PricingCriterion`) and Pricing Criterion Options (:model:`service_core.PricingCriterionOptions`) for a single Professional(:model:`professional.professional`)
    """
    professional = models.ForeignKey(Professional, on_delete=models.DO_NOTHING, related_name='pricing_criterions')
    pricing_criterion = models.ForeignKey('service_core.PricingCriterion', on_delete=models.DO_NOTHING, verbose_name='Tem critério')
    pricing_criterion_option = models.ManyToManyField('service_core.PricingCriterionOptions', verbose_name='Critérios')

    def __str__(self):
        return '{}'.format(self.id)


class DocumentType(BestPraticesModel):
    """
    Document Type used for Professional Documents(:model:`professional.ProfessionalDocument`)
    """
    name = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return '{}'.format(self.name)


class ProfessionalDocument(BestPraticesModel):
    """
    Stores the Documents for a single Professional(:model:`professional.professional`)
    """
    professional = models.ForeignKey(Professional, on_delete=models.DO_NOTHING, related_name='documentos')
    document = models.FileField(upload_to='professional/document/', default='professional/avatar/default.png')
    document_type = models.ForeignKey(DocumentType, on_delete=models.DO_NOTHING)

    def __str__(self):
        return '{}'.format(self.id)


class Schedule(BestPraticesModel):
    """
    Available time for a single Professional(:model:`professional.professional`)
    """
    daily_time_begin = models.TimeField()
    daily_time_end = models.TimeField()
    daily_date = models.DateField()
    professional = models.ForeignKey(Professional, on_delete=models.DO_NOTHING, related_name='schedules')
    attendance = models.ForeignKey('service_core.Attendance',null=True,blank=True)

    class Meta:
        verbose_name = "Schedule"

    def __str__(self):
        return '{}'.format(self.daily_date)


class FavoriteProfessional(BestPraticesModel):
    """
    Stores the Favorite Professional(:model:`professional.professional`) for a single Customer(:model:`customer.customer`)
    """
    customer = models.ForeignKey(Customer, on_delete=models.DO_NOTHING, related_name='professional_favorites')
    professional = models.ForeignKey(Professional, on_delete=models.DO_NOTHING, related_name='customer_favorites')

    class Meta:
        verbose_name = "Favorite Professional"

    def __str__(self):
        return '{}-{}'.format(self.customer, self.professional)


class ServiceProfessional(BestPraticesModel):
    """
    Stores the Services(:model:`service_core.service`) for a single Professional(:model:`professional.professional`)
    """
    service = models.ForeignKey('service_core.Service', verbose_name='Serviço')
    professional = models.ForeignKey(Professional, related_name='services')
    maximum_price = models.DecimalField(verbose_name="Preço Máximo", max_digits=12, decimal_places=2, default=0, blank=True)
    minimum_price = models.DecimalField(verbose_name="Preço (R$)", max_digits=12, decimal_places=2)
    average_time = models.PositiveIntegerField(verbose_name="Tempo Médio em minutos", default=0)
    enabled = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Service Professional"

    def __str__(self):
        return '{}'.format(self.id)

    @property
    def name_service(self):
        return "{}".format(self.service.name)

    def save(self, *args, **kwargs):
        service_professional = super(ServiceProfessional, self).save(*args, **kwargs)
        if self.service.pricing_criterion:
            pricing_criterions = self.service.pricing_criterion.options.all().order_by('id')
            professional_criterion = ProfessionalCriterion.objects.filter(
                    pricing_criterion=self.service.pricing_criterion, professional_id=self.professional)
            if professional_criterion.exists():
                professional_criterion = professional_criterion[0]
                pricing_criterions = professional_criterion.pricing_criterion_option.all()
            len_pricing_criterion = len(pricing_criterions)
            range_price_add = 0
            if len_pricing_criterion > 1:
                range_price_add = (self.maximum_price - self.minimum_price) / (len_pricing_criterion - 1)
            count = 0
            for option in pricing_criterions:
                option_query = ServiceProfessionalPricingCriterion.objects.filter(service_professional=self,
                                                                                  pricingcriterionoptions=option)
                new_price = round(self.minimum_price + (count * range_price_add), 0)
                if option_query.exists():
                    option_query.update(price=new_price, average_time=self.average_time)
                else:
                    pricing_criterion = ServiceProfessionalPricingCriterion(service_professional=self,
                                                                            pricingcriterionoptions=option,
                                                                            price=new_price,
                                                                            average_time=self.average_time)
                    pricing_criterion.save()
                count += 1
        return service_professional


class ServiceProfessionalLog(BestPraticesModel):
    """
    Stores price changes for Service Professional(:model:`professional.ServiceProfessional`)
    """
    service = models.ForeignKey('service_core.Service', verbose_name='Serviço', related_name='service_professional_old')
    professional = models.ForeignKey(Professional, related_name='services_old')
    maximum_price_old = models.DecimalField(verbose_name="Preço Máximo", max_digits=12, decimal_places=2, default=0,
                                        blank=True)
    minimum_price_old = models.DecimalField(verbose_name="Preço (R$)", max_digits=12, decimal_places=2)
    average_time_old = models.PositiveIntegerField(verbose_name="Tempo Médio em minutos", default=0)
    maximum_price = models.DecimalField(verbose_name="Preço Máximo", max_digits=12, decimal_places=2, default=0,
                                        blank=True)
    minimum_price = models.DecimalField(verbose_name="Preço (R$)", max_digits=12, decimal_places=2)
    average_time = models.PositiveIntegerField(verbose_name="Tempo Médio em minutos", default=0)

    class Meta:
        verbose_name = "Service Professional Log"

class ServiceProfessionalPricingCriterion(BestPraticesModel):
    """
    Stores the Price and Average Time for a Pricing Criterion Option(:model:`service_core.PricingCriterionOptions`) for a single Professional(:model:`professional.professional`)
    """
    service_professional = models.ForeignKey(ServiceProfessional, related_name='service_professional')
    pricingcriterionoptions = models.ForeignKey('service_core.PricingCriterionOptions')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    average_time = models.PositiveIntegerField(verbose_name="Tempo Médio em minutos", default=0)

    class Meta:
        verbose_name = "Service Professional Pricing Criterion"

    def __str__(self):
        return '{}-{}'.format(self.service_professional, self.pricingcriterionoptions)

    @property
    def name(self):
        return "{} {}".format(self.service_professional.service.name, self.pricingcriterionoptions.description)


class Badge(BestPraticesModel):
    """
    Model for Badges
    """
    description = models.CharField(max_length=40)
    picture = models.ImageField(upload_to='badges/', null=True, blank=True)

    class Meta:
        verbose_name = "Badge"

    def __str__(self):
        return '{}'.format(self.description)


class ProfessionalBadge(BestPraticesModel):
    """
    Stores the Badges(:model:`professional.Badge`) for a single Professional(:model:`professional.professional`)
    """
    badge = models.ForeignKey(Badge)
    professional = models.ForeignKey(Professional, on_delete=models.DO_NOTHING)

    class Meta:
        verbose_name = "Badges"

    def __str__(self):
        return '{}'.format(self.id)


class ProfessionalPicture(BestPraticesModel):
    """
    Stores the Avatar Picture for a single Professional(:model:`professional.professional`)
    """
    professional = models.ForeignKey(Professional, on_delete=models.DO_NOTHING)
    picture = models.ImageField(upload_to='professional/pictures/')
    picture_thumbnail = models.ImageField(upload_to='professional/thumbnail/')

    class Meta:
        verbose_name = "Professional Picture"

    def __str__(self):
        return '{}'.format(self.id)


class ProfessionalEvaluation(BestPraticesModel):
    """
    Stores an Attendance Evaluation for a single Professional(:model:`professional.professional`)
    """
    description = models.CharField(max_length=500, null=True, blank=True)
    rating = models.PositiveIntegerField()
    professional = models.ForeignKey(Professional, on_delete=models.DO_NOTHING)
    attendance = models.ForeignKey('service_core.Attendance', on_delete=models.DO_NOTHING, related_name='evaluation_professional_attendance')
    evaluation_type = models.ForeignKey('EvaluationType', null=True, blank=True)
    customer_choice = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Professional Evaluation"

    def __str__(self):
        return '{}'.format(self.description)


class EvaluationType(BestPraticesModel):
    """
    Evaluation Type used for Professional Evaluation(:model:`professional.ProfessionalEvaluation`)
    """
    description = models.CharField(max_length=40)
    picture = models.ImageField(upload_to='evaluations/', null=True, blank=True)
    picture_gray = models.ImageField(upload_to='evaluations/', null=True, blank=True)
    description_color = models.CharField(max_length=10, default='#FABA2C')

    class Meta:
        verbose_name = "EvaluationType"

    def __str__(self):
        return '{}'.format(self.description)


class Seller(BestPraticesModel, IuguMarketplaceAccount):
    """
    Model for Sellers
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='seller')
    executive = models.ForeignKey('Executive', related_name='executive', verbose_name='Executivo')
    observation = models.CharField(null=True, blank=True, max_length=2000)
    commission_percent = models.PositiveIntegerField(default=10, validators=[MaxValueValidator(25), MinValueValidator(0)])

    class Meta:
        verbose_name = "Vendedor"
        permissions = (('list_seller', 'Can list sellers'),
                       ('can_edit_executive', 'Can edit executive'))

    def save(self, *args, **kwargs):
        seller = super(Seller, self).save(*args, **kwargs)
        group = Group.objects.get(name='seller')
        self.user.groups.add(group)
        return seller

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)


class Executive(BestPraticesModel, IuguMarketplaceAccount):
    """
    Model for Executives
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='executive')
    cidades = models.ManyToManyField(City, through='ExecutiveCity', through_fields=['executive', 'city'])
    avatar = models.ImageField(upload_to='executive/avatar/', default='professional/avatar/default.png', blank=True)

    class Meta:
        verbose_name = "Executivo"
        permissions = (('list_executive', 'can view list of executives'),)

    def __str__(self):
        return '{} {}'.format(self.user.first_name, self.user.last_name)

    def save(self, *args, **kwargs):
        executive = super(Executive, self).save(*args, **kwargs)
        seller, created = Seller.objects.get_or_create(user=self.user, executive=self)
        seller.address=self.address
        seller.bank_account=self.bank_account
        seller.cellphone=self.cellphone
        seller.iugu_account_id=self.iugu_account_id
        seller.iugu_account_data=self.iugu_account_data
        seller.iugu_account_verification=self.iugu_account_verification
        seller.executive = self
        seller.save()
        professional, created = Professional.objects.get_or_create(user=self.user, executive=self, category_id=1)
        professional.avatar = self.avatar
        professional.address = self.address
        professional.bank_account = self.bank_account
        professional.celphone = self.cellphone
        professional.iugu_account_id = self.iugu_account_id
        professional.iugu_account_data = self.iugu_account_data
        professional.iugu_account_verification = self.iugu_account_verification
        professional.executive = self
        professional.is_test = True
        # professional.category_id = 1
        professional.save()
        group = Group.objects.get(name='executive')
        self.user.groups.add(group)
        return executive

    @property
    def get_citys(self):
        citys = ExecutiveCity.objects.filter(executive__pk=self.pk)
        return citys


class ExecutiveCity(models.Model):
    """
    Stores the Cities(:model:`core.city`) for a single Executive(:model:`professional.executive`)
    """
    executive = models.ForeignKey(Executive, on_delete=models.DO_NOTHING, related_name='citys')
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, verbose_name='Cidade')

    def __str__(self):
        return '{}'.format(self.id)

class Calendar():
    """
    Model for Calendar
    """

    def has_disponibility(self,professional, date, hour_inicial, hour_final):
        professional_schedules = Schedule.objects.filter(professional_id=professional,
                                                         daily_date=date,
                                                         daily_time_begin__lte=hour_inicial,
                                                         daily_time_end__gte=hour_final,
                                                         attendance__isnull=True)
        if professional_schedules.exists():
            return True
        return False

    def process_list(self,hour_blocks, hora_inicial, hora_final):
        final_blocks = []
        for block in hour_blocks:
            block_initial = block[0]
            block_final = block[1]
            if type(block_initial) == str:
                block_initial = time(*map(int, block_initial.split(':')))
            if type(block_final) == str:
                block_final = time(*map(int, block_final.split(':')))
            if hora_inicial >= block_initial and hora_final <= block_final:
                if block_initial != hora_inicial:
                    final_blocks.append([block_initial, hora_inicial])
                if block_final != hora_final:
                    final_blocks.append([hora_final, block_final])
            else:
                if hora_final > block_final and block_initial != time(0, 0, 0):
                    if (block_initial < hora_inicial) and (block_final < hora_inicial):
                        final_blocks.append([block_initial, block_final])
                    else:
                        final_blocks.append([block_initial, hora_inicial])
                else:
                    if block_initial > hora_final:
                        final_blocks.append([block_initial, block_final])
                    else:
                        final_blocks.append([hora_final, block_final])
        return final_blocks

    def process_calendar(self,professional, date, hour_inicial, hour_final, hour_range_inicial, hour_range_final):
        professional_sheddules = Schedule.objects.filter(professional_id=professional, daily_date=date, attendance__isnull=False)
        blocks = [[hour_inicial, hour_final]]
        for professional_sheddule in professional_sheddules:
            hora_inicial = professional_sheddule.daily_time_begin
            hora_final = professional_sheddule.daily_time_end
            blocks = self.process_list(blocks, hora_inicial, hora_final)
        for block in blocks:
            if block[1] > block[0]:
                schedule = Schedule(professional_id=professional, daily_date=date,
                                           daily_time_begin=block[0], daily_time_end=block[1])
                schedule.save()
        return blocks

    def process_full_calendar(self,professional, date):
        calendar = ProfessionalSchedule.objects.filter(professional_id=professional, date_schedule=date)
        professional_sheddules = Schedule.objects.filter(professional_id=professional, daily_date=date)
        professional_sheddules.filter(attendance__isnull=True).delete()
        if calendar:
            calendar = calendar.first()
            if calendar.provide_all_day:
                self.process_calendar(professional,date,time(7,0,0),time(22,0,0),time(0,0,0),time(23,59,59))
            else:
                if calendar.dawn_morning:
                    self.process_calendar(professional, date, calendar.dawn_morning_range_begin, calendar.dawn_morning_range_end,time(0,0,1),time(11,59,59))
                if calendar.afternoon_night:
                    self.process_calendar(professional, date, calendar.afternoon_night_range_begin, calendar.afternoon_night_range_end,time(11,59,59),time(23,59,59))
            professional_sheddules = Schedule.objects.filter(professional_id=professional, daily_date=date,
                                                             attendance__isnull=True)
            if Professional.objects.get(pk=professional).is_saloon:
                return 'success'
            for professional_sheddule in professional_sheddules:
                professional_sheddules_conflict = Schedule.objects.filter(professional_id=professional, daily_date=date,
                                                                          daily_time_end=professional_sheddule.daily_time_end,
                                                                          daily_time_begin__gt=professional_sheddule.daily_time_begin)
                if professional_sheddules_conflict.exists():
                    professional_sheddule.delete()
        return 'success'



class ProfessionalSchedule(BestPraticesModel):
    """
    Stores the Available Time for a single Professional(:model:`professional.professional`) can be edited by the User in the Professional App
    """
    professional = models.ForeignKey(Professional)
    provide_all_day = models.BooleanField(default=False)
    dawn_morning = models.BooleanField(default=False)
    afternoon_night = models.BooleanField(default=False)
    date_schedule = models.DateField()
    dawn_morning_range_begin = models.TimeField(default=time(0,0,0))
    dawn_morning_range_end = models.TimeField(default=time(0,0,0))
    afternoon_night_range_begin = models.TimeField(default=time(0,0,0))
    afternoon_night_range_end = models.TimeField(default=time(0,0,0))

    def __str__(self):
        return '{}'.format(self.date_schedule)

    def save(self, *args, **kwargs):
        profissional_schedule = super(ProfessionalSchedule, self).save(*args, **kwargs)
        c = Calendar()
        c.process_full_calendar(self.professional.pk,self.date_schedule)
        return profissional_schedule


class EvaluationCustomer(BestPraticesModel):
    """
    Stores an Attendance Evaluation for a single Customer(:model:`customer.customer`)
    """
    attendance = models.ForeignKey('service_core.Attendance', on_delete=models.CASCADE, related_name='attendance_evaluation_customer')
    cleaning = models.PositiveIntegerField(default=5)
    punctuality = models.PositiveIntegerField(default=5)
    accuracy = models.PositiveIntegerField(default=5)
    observation = models.CharField(null=True, blank=True, max_length=2000)

    def __str__(self):
        return '{}'.format(self.id)


class ProfessionalScheduleDefault(BestPraticesModel):
    """
    Stores the Default Schedule for a Professional(:model:`professional.professional`)
    """
    professional = models.ForeignKey(Professional)
    provide_all_day = models.BooleanField(default=False)
    dawn_morning = models.BooleanField(default=False)
    afternoon_night = models.BooleanField(default=False)
    day_of_week = models.CharField(max_length=20, choices=DAYS_OF_WEEK)
    dawn_morning_range_begin = models.TimeField(default=time(7,0,0))
    dawn_morning_range_end = models.TimeField(default=time(12,0,0))
    afternoon_night_range_begin = models.TimeField(default=time(13,0,0))
    afternoon_night_range_end = models.TimeField(default=time(19,0,0))

    def __str__(self):
        return '{}'.format(self.day_of_week)


class Contract(BestPraticesModel):
    """
    Contract for Professional(:model:`professional.professional`)
    """
    title = models.CharField(max_length=200, verbose_name='Modelo de Contrato', default='')
    #professional = models.ForeignKey(Professional)

    def __str__(self):
        return '{}'.format(self.title)


class ContractClause(BestPraticesModel):
    """
    Stores Clauses for the Contract(:model:`professional.contract`)
    """
    contract = models.ForeignKey(Contract)
    clause = models.CharField(max_length=200, verbose_name='Cláusula', default='')
    text = models.TextField(max_length=5000, null=True, blank=True, verbose_name='Texto')

    def __str__(self):
        return '{}'.format(self.clause)

class SaloonScheduleRemove(BestPraticesModel):
    """
    Available time for a single Professional(:model:`professional.professional`)
    """
    daily_time_begin = models.TimeField()
    daily_time_end = models.TimeField()
    daily_date = models.DateField()
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='remove_schedules')
    service_professional = models.ForeignKey(ServiceProfessional, related_name='remove_schedules')
    complete_date_end = models.DateTimeField(null=True, blank=True,
        verbose_name="Horário final "
    )

    class Meta:
        verbose_name = "ScheduleRemove"

    def __str__(self):
        return '{}'.format(self.daily_date)