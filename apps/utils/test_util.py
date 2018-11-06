import shutil
import os


def copy_test_files():
    source = './sample/tests'
    destination = './var/s3storage/media/test/'
    if os.path.exists(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)