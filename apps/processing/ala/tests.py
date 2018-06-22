from django.test import TestCase
from apps.processing.ala.models import SamplingFeature
from django.contrib.gis.geos import GEOSGeometry, Point


class SamplingFeatureTestCase(TestCase):
    def setUp(self):
        SamplingFeature.objects.create(
            id_by_provider="11359201",
            name="Brno",
            geometry=GEOSGeometry('POINT (1847520.94 6309563.27)', srid=3857)
        )

    def test_sampling_feature_exists(self):
        station = SamplingFeature.objects.get(name="Brno")
        self.assertEqual(station.name, 'Brno')

    def test_sampling_feature_exists_fail(self):
        station = SamplingFeature.objects.get(name="Brno")
        self.assertEqual(station.name, 'BrnoFail')
