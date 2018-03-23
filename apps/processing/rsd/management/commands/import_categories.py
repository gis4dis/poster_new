from django.db import models
from apps.importing.models import ProviderLog
from apps.processing.rsd.models import EventCategory
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET


class Command(BaseCommand):
    help = 'Create categories from events'

    def handle(self, *args, **options):
        categories = []
        for cat in EventCategory.objects.all():
            category = cat.name
            if not category in categories:
                    categories.append(category)

        for event in ProviderLog.objects.iterator():
            data = event.body
            tree = ET.fromstring(data)
            for tag in tree.iter('EVI'):
                code = tag.attrib["eventcode"]
                for tag in tag.iter('TXUCL'):
                    category = tag.text
                    if not category in categories:
                        categories.append(category)
                        cat = EventCategory(name=category,id_by_provider=code)
                        cat.save()
        print('Categories in database: {}'.format(categories))
        print('////////////////////')
        print('Number of categories: {}'.format(len(categories)))
        
