#__author__ = 'ambler'

import sys
import os
from multiprocessing import Process, Queue, JoinableQueue
from apps.YaDiskLib.YandexDiskRestClient import YandexDiskRestClient
from apps.YaDiskLib.YandexDiskException import YandexDiskException


def uploadF(cli):
    print()
    d = queue.qsize()
    while d > 0:
        z = queue.get()
        try:
            path = z.image.path
            print (path, os.getpid())

            cli.upload_file(path, "ZPA_Files/%s" % z.filename.upper() )
            z.on_cloud = True
            z.save()
            print ("%s uploaded" % z.filename)
        except YandexDiskException as e:
            if e.code == 409:
                print('EXISTS!!!')
                cli.remove_folder_or_file("ZPA_Files/%s" % z.filename.upper())
                print('REMOVED!!!')
                queue.put(z)
        except:
            pass


        queue.task_done()
        d = queue.qsize()



if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "zPhotoArchive.settings")

    from django.conf import settings
    import django
    django.setup()

    from apps.ZPhotoGallery.utils import *
    from apps.ZPhotoGallery.models import *


    dir_import = settings.ZPG_IMPORT_STORAGE
    dir_storage = settings.ZPG_DATA_STORAGE

    cli = YandexDiskRestClient(token = '')
    dsk = cli.get_disk_metadata()

    # забираем из облака
    print('expot from Cloud')
    imdirs = []
    for id in imdirs:
        getCloudRidData(id, cli, dir_import)

    print('import to PhotoArchive')
    # импортируем в фотоархив
    s=scanImportFolder(i_dir=dir_import, result=[], dir_storage = dir_storage, dir_import=dir_import)
    print(s)


    #upload to cloud
    print('import to Cloud')
    queue = JoinableQueue()
    pr = 1
    pro = []

    for z in ZPGFile.objects.filter(is_movie=0, on_cloud=0).order_by("file_date"):
        queue.put(z)

    for i in range(pr):
        p = Process(target=uploadF, args=(cli,))
        p.daemon = True
        p.start()
        pro.append(p)

    queue.join()

    for p in pro:
        p.join()


    # бекапим файл с бд
    dbfile_path = settings.DATABASES['default']['NAME']
    dbfile_name = settings.DATABASES['default']['NAME'].split('/')[-1]


    cli.move_folder_or_file(dbfile_name, dbfile_name+"_old")
        #remove_folder_or_file(dbfile_name)
    cli.upload_file(dbfile_path, dbfile_name )

    print ("DB file uploaded")

