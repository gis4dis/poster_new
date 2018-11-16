import os
from datetime import datetime, timedelta
from dateutil.rrule import rrule, DAILY

from django.conf import settings
from django.core.files.storage import default_storage


def check_ftp_uploads():
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    month_ago = today - timedelta(days=30)

    top_level_dir = os.path.normpath(settings.IMPORT_ROOT + '/apps.processing.pmo/')
    if not top_level_dir.endswith("/"):
        top_level_dir += "/"

    error_dict = {}

    # Populate for last 30 days
    for day in list(rrule(DAILY, dtstart=month_ago, until=yesterday)):
        error_dict[date_to_ymd(day)] = 0

    # For every directory in proper folder
    for daily_dir in default_storage.listdir(top_level_dir):
        # Skip files
        if not daily_dir.is_dir:
            print("{file} is not directory, but file. Skipping".format(file=daily_dir.object_name))
            continue

        datetime_obj = path_to_date(daily_dir.object_name)

        # Skip old directories and today
        if datetime_obj < month_ago or datetime_obj > yesterday:
            continue

        # Count number of files in directory (need to do for loop, since Minio Storage is generator)
        counter = 0
        for _ in default_storage.listdir(daily_dir.object_name):
            counter += 1

        # On monday
        if datetime_obj.weekday() == 0:
            # We should have 5 records
            if counter == 5:
                del error_dict[date_to_ymd(datetime_obj)]
            else:
                error_dict[date_to_ymd(datetime_obj)] = counter
        # On any other day
        else:
            # We should have 2
            if counter == 2:
                del error_dict[date_to_ymd(datetime_obj)]
            else:
                error_dict[daily_dir.object_name] = counter

    return error_dict


def path_to_date(path):
    format_str = '%Y%m%d'
    ymd_string = path.strip("/").split("/")[-1]
    return datetime.strptime(ymd_string, format_str)


def date_to_ymd(date):
    format_str = '%Y%m%d'
    return date.strftime(format_str)
