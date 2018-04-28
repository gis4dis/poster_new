# coding=utf-8
from apps.processing.ozp.models import SamplingFeature, Observation
from apps.common.models import Process, Property
from apps.utils.obj import *
from django.contrib.gis.geos import GEOSGeometry, Point


stations_def = [
    ('Arboretum', {'name': u'Arboretum','geometry': GEOSGeometry('POINT (1849713.38 6311063.58)', srid=3857)}),
    ('Lány', {'name': u'Lány','geometry': GEOSGeometry('POINT (1846062.32 6302764.00)', srid=3857)}),
    ('Svatoplukova', {'name': u'Svatoplukova','geometry': GEOSGeometry('POINT (1852553.47 6309762.61)', srid=3857)}),
    ('Výstaviště', {'name': u'Výstaviště', 'geometry': GEOSGeometry('POINT (1844439.17 6306893.18)', srid=3857)}),
    ('Zvonařka', {'name': u'Zvonařka','geometry': GEOSGeometry('POINT (1849962.51 6306633.61)', srid=3857)}),
]

def get_or_create_ozp_stations():
    return get_or_create_objs(SamplingFeature, stations_def, 'id_by_provider')
