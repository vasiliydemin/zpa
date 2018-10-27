#__author__ = 'ambler'

import sys
import os
from multiprocessing import Process, Queue, JoinableQueue
from apps.YaDiskLib.YandexDiskRestClient import YandexDiskRestClient
from apps.YaDiskLib.YandexDiskException import YandexDiskException
from tokenlo import *

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ZFotoArchive.settings")

    from django.conf import settings
    import django
    django.setup()

    from apps.ZPhotoGallery.utils import *
    from apps.ZPhotoGallery.models import *

    dir_import = settings.ZPG_IMPORT_STORAGE
    dir_storage = settings.ZPG_DATA_STORAGE

    cli = YandexDiskRestClient(token = local_token())
    dsk = cli.get_disk_metadata()

    # забираем из облака
    print('expot from Cloud')
    imdirs = local_dirs()

    for item in cli.get_content_of_folder(imdirs[1]).children:
        print (item.md5, item.type, item.path)