from django.db import models
from apps.common.models import Property, Process
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create observed property & process for events'

    def handle(self, *args, **options):
        try:
            prop = Property.objects.get(name_id='occuring_events')
            prop.name="occuring events"
            prop.save()
        except:
            prop = Property(
                name_id='occuring_events',
                name='occuring events',
                unit=''
                )
            prop.save()
        try:
            proc = Process.objects.get(name_id='observation')
            proc.name="observation"
            proc.save()
        except:
            proc = Process(
                name_id='observation',
                name='observation',
                )
            proc.save()
        print('Metadata for EventObservations imported')