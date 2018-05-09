from django.db import models
from apps.common.util.util import processes_def, props_def
from apps.utils.obj import *
from apps.common.models import Property, Process
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create observed property & process for events'

    def handle(self, *args, **options):
        get_or_create_processes()
        get_or_create_props()
        print('Metadata for EventObservations imported')


def get_or_create_props():
    for prop in props_def:
        if 'default_mean' in prop[1]:
            mean = prop[1]['default_mean']
            if not isinstance(prop[1]['default_mean'], Process):
                mean_process = Process.objects.get(name_id=mean)
                if mean and mean_process:
                    prop[1]['default_mean'] = mean_process
                else:
                    prop[1]['default_mean'] = None

    return get_or_create_objs(Property, props_def, 'name_id')


def get_or_create_processes():
    return get_or_create_objs(Process, processes_def, 'name_id')