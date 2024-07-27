from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from auctions.models import Notification,RegistrationFeeTransaction
from django_celery_beat.models import CrontabSchedule, PeriodicTask
import json



User = settings.AUTH_USER_MODEL


@receiver(post_save, sender=User)
def send_user_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(user=instance, message="Your account has been created successfully.")
        RegistrationFeeTransaction.objects.create(
            user=instance,
        )
        