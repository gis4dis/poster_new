import os
from datetime import datetime, timedelta
from django.conf import settings
from django.core.files.storage import default_storage

def check_downloads():
    today = datetime.now()

    yesterday = today - timedelta(days=1)
    top_level_dir = os.path.normpath(settings.IMPORT_ROOT + '/apps.processing.pmo/')

    if not top_level_dir.endswith("/"):
        top_level_dir += "/"

    ymd = date_to_ymd(yesterday)
    daily_dir = top_level_dir + ymd + '/'

    response_dict = {}

    counter = 0
    for _ in default_storage.listdir(daily_dir):
        counter += 1

    response_dict['downloaded_files-1'] = counter
    response_dict['directory'] = daily_dir
    response_dict['date'] = yesterday

    missingFiles = []
    filesToCheck = []
    if yesterday.weekday() == 0:
        if counter >= 5:
            response_dict['dowloaded_files-1-result'] = 'ok'
        else:
            response_dict['dowloaded_files-1-result'] = 'wrong_files_count'

        filesToCheck = ['HOD.dat', 'jakost.dat', 'nadrzsae.dat', 'POD.dat', 'srazsae.dat']
    else:
        if counter >= 2:
            response_dict['dowloaded_files-1-result'] = 'ok'
        else:
            response_dict['dowloaded_files-1-result'] = 'wrong_files_count'
        filesToCheck = ['nadrzsae.dat', 'POD.dat']

    for file in filesToCheck:
        if not default_storage.exists(daily_dir + '/' + file):
            missingFiles.append(file)

    if len(missingFiles) > 0:
        response_dict['dowloaded_files-1-result'] = 'Missing files: ' + ', '.join(missingFiles)

    return response_dict


def path_to_date(path):
    format_str = '%Y%m%d'
    ymd_string = path.strip("/").split("/")[-1]
    return datetime.strptime(ymd_string, format_str)


def date_to_ymd(date):
    format_str = '%Y%m%d'
    return date.strftime(format_str)
