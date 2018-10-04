from __future__ import absolute_import, unicode_literals
from django.core.management.base import BaseCommand
from apps.processing.pmo.tasks import import_observations


class Command(BaseCommand):
    help = 'GetLastRecordDate '

    def handle(self, *args, **options):
        import_observations()