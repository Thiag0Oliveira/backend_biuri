from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from datetime import datetime, timedelta
from .models import Attendance
from apps.after_sale.tasks import after_sale_cancelation_by_professional
from .tasks import whatsapp_message, pixel_feedback


@receiver(post_save, sender=Attendance)
def cancelation_after_sale(sender, instance, **kwargs):
    if instance.scheduling_date:
        time_danger = datetime.now() - instance.scheduling_date
        if (instance.status == 'canceled_by_professional' and time_danger < timedelta(hours=2)):
            after_sale_cancelation_by_professional(attendance=instance)


@receiver(post_save, sender=Attendance)
def cancelation_after_sale(sender, instance, **kwargs):
    try:
        status = {'draft': 'Rascunho',
                  'complete_draft': 'Rascunho Completo',
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
                  'rejected': 'Rejeitado'}
        if instance.status != 'draft' and not instance.is_test:
            # if (instance.professional):
                # if instance.professional.executive:
            message_text = '*Atendimento número {}*'.format(instance.pk)
            if instance.type == 'has_preference':
                message_text += '\n*Tipo:* ' + 'Agendamento Direto'
            else:
                message_text += '\n*Tipo:* ' + 'Click Biuri'
            if instance.professional:
                message_text += '\n*Profissional:* ' + str(instance.professional.full_name)
            if instance.customer:
                message_text += '\n*Cliente:* {}'.format(instance.customer.user.first_name)
            message_text += '\n*Status:* ' + status[instance.status]
            message_text += '\n*Serviço:* {}'.format(instance.initial_service.name)
            if instance.scheduling_date:
                message_text += '\n*Horário:* ' + str(instance.scheduling_date)
            address = instance.address
            if address:
                message_text += '\n*Endereço:* {}, {} - {} {}'.format(address.address, address.number, address.neighborhood, address.city)
            url = '\n*Link:*  http://www.biuri.com.br/after_sale/attendance/{}/edit'.format(instance.pk)
            message_text += url
            if not settings.DEBUG:
                whatsapp_message.delay(text=message_text)
        if instance.status == 'waiting_confirmation':
            if not settings.DEBUG:
                pixel_feedback.delay(instance.pk, 'Purchase')
        if instance.status == 'draft' and instance.scheduling_date is not None:
            if not settings.DEBUG:
                pixel_feedback.delay(instance.pk, 'InitiateCheckout')
    except:
        pass