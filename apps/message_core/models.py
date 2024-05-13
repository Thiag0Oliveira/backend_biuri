from django.contrib.auth.models import User
from django.db import models

from apps.common.models import BestPraticesModel


# Create your models here.
from apps.common.views import Sms
from apps.service_core.views import Notification



GENDER_LIST = (
    ('all', 'Masculino e Feminino'),
    ('male', 'Masculino'),
    ('female', 'Feminino'),
)


class PushToken(BestPraticesModel):
    """
    Model for a User's Push Token
    """
    user = models.ForeignKey(User)
    token = models.CharField(max_length=200)

    def __str__(self):
        return self.token


class Message(BestPraticesModel):
    """
    Model for Messages
    """
    text = models.CharField(max_length=200)
    destination = models.TextField(max_length=5000, null=True, blank=True)
    type = models.CharField(max_length=20, choices=[('sms','SMS'),('sms_multiple','SMS VÁRIOS'),('push', 'PUSH NOTIFICATION'),('push_multiple', 'PUSH NOTIFICATION VÁRIOS'), ('whatsapp', 'WHATSAPP')])
    is_success = models.BooleanField(default=False)
    count = models.PositiveIntegerField(default=0)
    send = models.BooleanField(default=True)
    data = models.TextField(max_length=5000, default='{}', null=True, blank=True)

    def list_to(self):
        return self.destination.replace('"', '').strip('][').split(',')

    def count_to(self):
        return len(self.list_to())

    def save(self, *args, **kwargs):
        if self.send:
            if self.type == 'sms':
                data = {'to': str(self.destination),
                        'from': 'BIURI: ',
                        'msg': self.text}
                sms = Sms()
                try:
                    sms.send(data=data)
                    self.is_success = True
                    self.send = False
                except:
                    pass
            elif self.type == 'push':
                notification = Notification()
                n = notification.push(
                    data=self.data,
                    to=self.destination,
                    title='Biuri',
                    body=self.text
                )
                self.is_success = True
                self.send = False
                self.count = self.count_to()
            elif self.type == 'push_multiple':
                notification = Notification()
                n = notification.push(
                    data=self.data,
                    to=self.list_to(),
                    title='Biuri',
                    body=self.text,
                    multiple=True
                )
                self.is_success = True
                self.send = False
                self.count = self.count_to()
            elif self.type == 'sms_multiple':
                data = []
                for i in self.list_to():
                    data.append({'to': i,
                            'from': 'BIURI: ',
                            'msg': self.text})
                try:
                    sms = Sms()
                    sms.send(data=data, multiple=True)
                    self.is_success = True
                    self.send = False
                except:
                    pass
        return super(Message, self).save(*args, **kwargs)


class News(BestPraticesModel):
    """
    Model for News
    """
    title = models.CharField(max_length=30)
    picture_client = models.ImageField(upload_to='news/', verbose_name='Picture Client', null=True, blank=True)
    picture = models.ImageField(upload_to='news/', verbose_name='Picture Professional', null=True, blank=True)
    date = models.DateField()
    place = models.CharField(max_length=20)
    url = models.URLField()
    is_active = models.BooleanField(default=True)
    is_global = models.BooleanField(default=False)
    citys = models.ManyToManyField('core.City', blank=True)
    public = models.CharField(max_length=20, default='all', choices=[('all','Todos'),
                                                      ('professional', 'Profissional'),
                                                      ('client', 'Cliente')])

    def __str__(self):
        return "{}".format(self.title)


class PushSchedule(BestPraticesModel):
    """
    Model for Push Schedule
    """
    title = models.CharField(max_length=40)
    text = models.CharField(max_length=200)
    date_schedule = models.DateTimeField()
    send_professional = models.BooleanField(default=False)
    professional_gender = models.CharField(max_length=20, choices=GENDER_LIST, null=True, blank=True, verbose_name='Sexo dos Profissionais')
    professional_categories = models.ManyToManyField('service_core.Category', blank=True)
    send_customer = models.BooleanField(default=False)
    customer_gender = models.CharField(max_length=20, choices=GENDER_LIST, null=True, blank=True, verbose_name='Sexo dos Clientes')
    send_region = models.BooleanField(default=False)
    has_sended = models.BooleanField(default=False)
    executive = models.ForeignKey('professional.Executive', on_delete=models.DO_NOTHING,null=True, blank=True)
    cidades = models.ManyToManyField('core.City')


class PushScheduleCity(models.Model):
    """
    Stores the Cities(:model:`core.city`) for a Push Schedule(:model:`message_core.pushSchedule`)
    """
    push_schedule = models.ForeignKey(PushSchedule, on_delete=models.DO_NOTHING)
    city = models.ForeignKey('core.City', on_delete=models.DO_NOTHING, verbose_name='Cidade')
    neighborhoods = models.ManyToManyField('core.Neighborhood', verbose_name='Bairros')

    def __str__(self):
        return '{}'.format(self.id)
#