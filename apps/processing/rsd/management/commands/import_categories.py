from django.db import models
from apps.importing.models import ProviderLog
from apps.processing.rsd.models import EventCategory
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET


class Command(BaseCommand):
    help = 'Create categories from events'

    def handle(self, *args, **options):
        
        # EventCategory.objects.all().delete()
        
        categories = []
        for cat in EventCategory.objects.all():
            category = cat.id_by_provider
            if not category in categories:
                    categories.append(category)

        for event in ProviderLog.objects.iterator():
            data = event.body
            tree = ET.fromstring(data)
            for msg in tree.iter('MSG'):
                for tag in msg.iter('EVI'):
                    code = tag.attrib["eventcode"]
                    category = ""
                    for text in tag.iter('TXUCL'):
                        group = text.text
                        break
                    for name in tag.iter('TXEVC'):
                        code_name = name.text
                        break
                            
                    if not code in categories:
                        categories.append(code)
                        cat = EventCategory(group=group, name=code_name,id_by_provider=code)
                        cat.save()
        print('Categories in database: {}'.format(categories))
        print('////////////////////')
        print('Number of categories: {}'.format(len(categories)))

        
                