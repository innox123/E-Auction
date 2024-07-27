import json
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django_celery_beat.models import PeriodicTask, CrontabSchedule


@receiver(post_save, sender=Auction)
def task_maker(sender, instance, created, **kwargs):
    if created:
        schedule, created = CrontabSchedule.objects.get_or_create(
            minute=instance.end_at.minute,
            hour=instance.end_at.hour,
            day_of_month=instance.end_at.day,
            month_of_year=instance.end_at.month,
        )
        PeriodicTask.objects.create(
            crontab=schedule,
            name="Auction" + str(instance.id),
            task="auctions.tasks.end_auction_task",
            args=json.dumps((str(instance.id),))
        )

@receiver(post_save, sender=Item)
def create_specification(sender, instance, created, **kwargs):
    if created:
        Specification.objects.create(
            item=instance
        )
