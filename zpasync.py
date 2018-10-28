#__author__ = 'ambler'

import sys
import os
from multiprocessing import Process, Queue, JoinableQueue
from apps.YaDiskLib.YandexDiskRestClient import YandexDiskRestClient
from apps.YaDiskLib.YandexDiskException import YandexDiskException
from tokenlo import *


if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zPhotoArchive.settings")

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
    export_from_cloud(local_dirs(),cli, dir_import)

    # импортируем в фотоархив
    #print('import to PhotoArchive')
    import_to_zpa(dir_storage = dir_storage, dir_import=dir_import)
    #s=scanImportFolder(i_dir=dir_import, result=[], dir_storage = dir_storage, dir_import=dir_import)




















