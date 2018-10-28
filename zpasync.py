#__author__ = 'ambler'

import sys
import os
from multiprocessing import Process, Queue, JoinableQueue
from apps.YaDiskLib.YandexDiskRestClient import YandexDiskRestClient
from apps.YaDiskLib.YandexDiskException import YandexDiskException
from tokenlo import *

def save_cloud_file(clofile, cli=None, dir_import=''):
    save_path = os.path.join(dir_import, 'CLOUD', *clofile.path.split('/')[1:-1])
    print(save_path)

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    ur = cli.get_download_link_to_file(clofile.path)
    r = requests.get(ur['href'], stream=True)
    if r.status_code == 200:
        with open(os.path.join(save_path, clofile.filename), 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    del r

def save_ZPGCloudFile(item):
    cfile = ZPGCloudFile()
    cfile.filename = item.name
    cfile.hash = item.md5
    cfile.mime_type = item.mime_type
    cfile.path = item.path
    cfile.preview = item.preview
    cfile.size = item.size
    cfile.save()




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
    imdirs = local_dirs()

    for dirs in []: #local_dirs():
        for item in cli.get_content_of_folder(dirs).children:
            print (item.md5, item.type, item.path)
            if not ZPGCloudFile.objects.filter(hash=item.md5):
                save_ZPGCloudFile(item)

    for cloit in ZPGCloudFile.objects.filter(is_loaded=False)[:100]:
        print(cloit.filename)
        save_cloud_file(cloit, cli, dir_import)
        cloit.is_loaded = True
        cloit.save()