from django.db import models
from apps.importing.models import ProviderLog
from datetime import datetime, date, timedelta
from dateutil.parser import parse
from dateutil import relativedelta
from django.core.management.base import BaseCommand
import xml.etree.ElementTree as ET
from apps.utils.time import UTC_P0100
import json

class Command(BaseCommand):
    help = 'Saves all accidents on D1 to json file.'

    def handle(self, *args, **options):

        collection = {
                        "type": "FeatureCollection",
                        "features": []
                    }
        i = 0
        for event in ProviderLog.objects.iterator():

            data = event.body
            tree = ET.fromstring(data)

            end = True
            for cat in tree.iter('TXUCL'):
                if(cat.text == 'Nehody'):
                    end = False

            if(end):
                continue
            features = []
            
            for tag in tree.iter('DEST'):
                road = tag.find('ROAD')
                is_d1 = False
                if road is not None and 'RoadNumber' in road.attrib:
                    is_d1 = True if road.attrib['RoadNumber'] == 'D1' else False
                town_ship = tag.attrib['TownShip']
                if((town_ship == 'Brno-venkov' or town_ship == 'Brno-město') or (is_d1)):
                    for tag in tree.iter('TSTA'):
                        start_time = parse(tag.text)
                    for tag in tree.iter('TSTO'):
                        end_time = parse(tag.text)

                    start_time = start_time.astimezone(UTC_P0100)
                    end_time = end_time.astimezone(UTC_P0100)

                    if(end_time < start_time):
                        start_time, end_time = end_time, start_time

                    for tag in tree.iter('COORD'):
                        coord_x = tag.attrib['x']
                        coord_y = tag.attrib['y']

                    i += 1
                    collection.get('features').append({
                                "type": "Feature",
                                "id": str(i),
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": 
                                        [float(coord_y), float(coord_x)]
                                },
                                "properties": {
                                    "start_time": str(start_time),
                                    "end_time": str(end_time)
                                }
                            })
                    
                    end = False
                else:
                    end = True
                    break
            if(end):
                continue
        print(i)
        new = json.dumps(collection)
        with open('var/nehody.json', 'w') as the_file:
            the_file.write(new)
