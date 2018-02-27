from django.db import models
from apps.importing.models import ProviderLog
from apps.processing.rsd.models import EventCategory
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET


class Command(BaseCommand):
    help = 'Create categories from events'

    def handle(self, *args, **options):
        categories = []
        EventCategory.objects.all().delete()
        for event in ProviderLog.objects.iterator():
            data = event.body
            tree = ET.fromstring(data)
            for tag in tree.iter('TXUCL'):
                category = tag.text
                if not category in categories:
                    categories.append(category)
                    cat = EventCategory(category=category)
                    cat.save()


        print((categories))
            
