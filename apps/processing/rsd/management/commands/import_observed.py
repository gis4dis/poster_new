from django.db import models
from apps.common.util.util import get_or_create_processes, get_or_create_props
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create observed property & process for events'

    def handle(self, *args, **options):
        get_or_create_processes()
        get_or_create_props()
        print('Metadata for EventObservations created')