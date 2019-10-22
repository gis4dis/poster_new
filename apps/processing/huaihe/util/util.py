# coding=utf-8
from apps.processing.huaihe.models import SamplingFeature
from apps.utils.obj import *
from django.contrib.gis.geos import GEOSGeometry

# select st_astext(st_transform(st_setsrid(ST_GeomFromText('POINT(114.7359 32.3255)'), 4326), 3857))
stations_def = [
    ('50100500', {'name': u'Xixian Station', 'geometry': GEOSGeometry('POINT(12772341.96 3806113.80)', srid=3857)}),
]


def get_or_create_huaihe_stations():
    return get_or_create_objs(SamplingFeature, stations_def, 'id_by_provider')
