from apps.importing.models import ProviderLog
import xml.etree.ElementTree as ET
from datetime import datetime
import os


def import_provider_logs(provider):
    received_time = datetime(2018, 3, 23, 10, 30, 00)
    
    
    body = xml_to_str('logs/log_1.xml')

    ProviderLog.objects.create(
        provider=provider,
        is_valid=True,
        content_type='text/xml',
        body=body,
        file_name='abc',
        file_path='/opt/poster-app/import/rsd/2018/03/20180323-093033_valid_abc_4fd9d424-a081-463f-8e90-351737e033b5.txt',
        ext='txt',
        received_time=received_time,
        uuid4='d85a4f5a-fd7f-4f62-9d76-f8ebd4c86a10',
        last_processed=None,
    )

    body = xml_to_str('logs/log_outside_extent.xml')

    ProviderLog.objects.create(
        provider=provider,
        is_valid=True,
        content_type='text/xml',
        body=body,
        file_name='abc',
        file_path='/opt/poster-app/import/rsd/2018/03/20180323-093033_valid_abc_4fd9d424-a081-463f-8e90-351737e033b4.txt',
        ext='txt',
        received_time=received_time,
        uuid4='d85a4f5a-fd7f-4f62-9d76-f8ebd4c86a11',
        last_processed=None,
    )

    body = xml_to_str('logs/log_1_changed_category.xml')

    ProviderLog.objects.create(
        provider=provider,
        is_valid=True,
        content_type='text/xml',
        body=body,
        file_name='abc',
        file_path='/opt/poster-app/import/rsd/2018/03/20180323-093033_valid_abc_4fd9d424-a081-463f-8e90-351737e033b1.txt',
        ext='txt',
        received_time=received_time,
        uuid4='d85a4f5a-fd7f-4f62-9d76-f8ebd4c86a12',
        last_processed=None,
    )

    body = xml_to_str('logs/log_out_of_time.xml')
    received_time = datetime(2018, 3, 24, 0, 0, 1)
    ProviderLog.objects.create(
        provider=provider,
        is_valid=True,
        content_type='text/xml',
        body=body,
        file_name='abc',
        file_path='/opt/poster-app/import/rsd/2018/03/20180323-093033_valid_abc_4fd9d424-a081-463f-8e90-351737e033c1.txt',
        ext='txt',
        received_time=received_time,
        uuid4='d85a4f5a-fd7f-4f62-9d76-f8ebd4c86a14',
        last_processed=None,
    )
    return True



dir_path = os.path.dirname(os.path.realpath(__file__))

def xml_to_str(path):
    root = ET.parse(os.path.join(dir_path, path)).getroot()
    body = ET.tostring(root, encoding='unicode', method='xml')
    return body