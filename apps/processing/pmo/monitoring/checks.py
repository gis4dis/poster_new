import os

from django.conf import settings
from django.core.files.storage import default_storage


def check_ftp_uploads():

    top_level_dir = os.path.normpath(settings.IMPORT_ROOT + '/apps.processing.pmo/')
    if not top_level_dir.endswith("/"):
        top_level_dir += "/"

    check_dict = {}

    for daily_dir in default_storage.listdir(top_level_dir):
        if not daily_dir.is_dir:
            print("{directory} is not directory, but file. Skipping".format(directory=daily_dir.object_name))
            continue

        check_dict[daily_dir.object_name] = 0
        for downloaded_file in default_storage.listdir(daily_dir.object_name):
            check_dict[daily_dir.object_name] += 1

    print(check_dict)