
try:
    from .src.YandexDiskRestClient import YandexDiskRestClient
except:
    from src.YandexDiskRestClient import YandexDiskRestClient

import pyminizip

cli = YandexDiskRestClient(token = '6b11a6b8bffa4f36b9b49cdbf327f624')

print(cli.get_disk_metadata())


pyminizip.compress('/mnt/d_drive/PHOTO_STORAGE/2002/01/20020122085702866649.jpg',
                   '/mnt/d_drive/PHOTO_STORAGE/2002/01/20020122085702866649t.zip',
                   '123',
                   9)



cli.upload_file('/mnt/d_drive/PHOTO_STORAGE/2002/01/20020122085702866649t.zip', '20020122085702866649t.zip')

import os

os.remove('/mnt/d_drive/PHOTO_STORAGE/2002/01/20020122085702866649t.zip')

"""
cli.create_folder('Foto')

dr = '/mnt/d_drive/PHOTO_STORAGE/2002/01/'

import os
for dirname, dirnames, filenames in os.walk(dr):
    for fn in filenames:
        print('%s%s' % (dr,fn))
        cli.upload_file('%s%s' % (dr,fn), 'Foto/%s' % fn)



"""