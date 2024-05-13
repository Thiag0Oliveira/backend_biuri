from django.contrib.auth.models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=User)
def save_profile(sender, instance, **kwargs):
    if instance.username == "":
        instance.username = instance.email
        instance.save()