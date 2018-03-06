from django.db import models
from apps.common.models import Property, Process
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create observed property & process for events'

    def handle(self, *args, **options):
        prop = Property(
            name_id='occuring_events',
            name='Occuring events',
            unit=''
            )
        prop.save()
        
        proc = Process(
            name_id='observation',
            name='Observation',
            )
        proc.save()
        