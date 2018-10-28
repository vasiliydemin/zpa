# -*- coding: utf-8 -*-
__author__ = 'ambler'

import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import date
import os.path, time, datetime
import shutil
import hashlib
import requests
from .models import *
import subprocess
import re


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
    clofile.is_loaded = True
    clofile.save()


def save_ZPGCloudFile(item):
    if not ZPGCloudFile.objects.filter(hash=item.md5):
        cfile = ZPGCloudFile()
        cfile.filename = item.name
        cfile.hash = item.md5
        cfile.mime_type = item.mime_type
        cfile.path = item.path
        cfile.preview = item.preview
        cfile.size = item.size
        cfile.save()

def export_from_cloud(dirs, cli, dir_import):
    for dirs in dirs:
        for item in cli.get_content_of_folder(dirs).children:
            print (item.md5, item.type, item.path)
            save_ZPGCloudFile(item)

    for cloit in ZPGCloudFile.objects.filter(is_loaded=False)[:10]:
        print(cloit.filename)
        save_cloud_file(cloit, cli, dir_import)


def import_to_zpa(dir_storage, dir_import):

    print(dir_storage)
    for item in os.listdir(dir_storage):
        item_path = os.path.join(dir_storage, item)
        print (item_path)

        if os.path.isdir(item_path) == True:
            import_to_zpa(item_path, dir_import)
        else:
            item_hash = getItemHash(item_path)

            if ZPGFile.objects.filter(hash=item_hash):
                zfile = ZPGFile()

                exif = get_exif_data(item_hash)
                zfile.file_date = get_datetime_from_exif(item_path, exif) or get_datetime_from_file(item_path) or get_datetime_from_path(item_path)
                zfile.ext = item.split('.')[-1]
                zfile.filename = '%s%s.%s' % (zfile.file_date.strftime('%Y%m%d%H%M%S'), str(time.time())[6:].replace('.', ''), zfile.ext)
                zfile.orig_path = item_path
                zfile.size=os.path.getsize(item_path)
                zfile.hash = item_hash
                zfile.camera=get_camera_from_exif(exif)
                zfile.image.name = '%s/%s' % (zfile.file_date.strftime('%Y/%m'), zfile.filename)

                hw_isv = getItemSize(ItemPath)

                zfile.width, zfile.height = hw_isv[0]
                if hw_isv[0]!=(0,0):
                    zfile.is_movie = hw_isv[1]
                else:
                    zfile.is_movie = 0


                #print zfile.width, zfile.height
                savedfile = copyFileToStorage(data = data, istorage = dir_storage)

                if savedfile[0]:
                    if savedfile[1]:
                        zfile.width, zfile.height = zfile.height, zfile.width
                    #print zfile.width, zfile.height
                    zfile.save()
                    print ('saved')
                    imported_cnt =+ 1
                    for kw in getKWfromPath(path = ItemPath, fdir = dir_import):
                        zfile.tags.add(kw)
                    zfile.save()

                else:
                    print ('no save')
                    del zfile
            else:
                print('exists')


def get_camera_from_exif(exif={}):
    camera = ''
    if exif.keys():
        camera = "%s-%s" % (exif.get('Make', 'camera'), exif.get('Model', 'xz'))
        camera = camera.replace('\x00','')
        camera = re.sub(' +',' ',camera)
    return camera


def get_datetime_from_file(file):
    return datetime.datetime.fromtimestamp(os.path.getmtime(file))


def get_datetime_from_exif(file, exif={}):
    dt = None
    if exif.keys():
        dt = exif.get('DateTimeDigitized', exif.get('DateTimeOriginal', exif.get('DateTime', None)))
        if dt != '0000:00:00 00:00:00':
            try:
                dt = datetime.datetime.strptime(dt, '%Y:%m:%d %H:%M:%S')
            except:
                dt = None
        else:
            dt = None
    return dt


def get_datetime_from_path(path):
    re1= re.compile(r'(\d{2})[\.\:\-\/](\d{4})')
    re2= re.compile(r'(\d{4})[\.\:\-\/](\d{2})')
    re3= re.compile(r'(.*)(\d{4}).*')
    gg = path.split('/')
    gg.reverse()

    dt = {'m':1, 'y':1900, 'd':1}

    for pf in gg[1:]:
        ptt = re1.findall(pf)
        if ptt:
            dt['m'] = ptt[0][0]
            dt['y'] = ptt[0][1]

        ptt = re2.findall(pf)
        if ptt:
            dt['m'] = ptt[0][1]
            dt['y'] = ptt[0][0]

        ptt = re3.findall(pf)
        if ptt:
            dt['y'] = ptt[0][1]

        if dt['y'] != 1900:
            break

    dt['m'] = int(dt['m'])
    dt['y'] = int(dt['y'])

    if dt['y'] != 1900:
        dt_st = '%s-%s-%s' % (dt['y'], dt['m'], dt['d'])
        ddt = datetime.datetime.strptime(dt_st, '%Y-%m-%d')
    else:
        ddt = None
    return ddt


def get_exif_data(file):
    exif = dict()
    try:
        img = Image.open(file)
        try:
            exif_data = img._getexif()
        except:
            exif_data = None
        if exif_data:
            for k,v in img._getexif().items():
                if TAGS.get(k, None):
                    exif[TAGS[k]] = v
    except:
        pass
    return exif


def getItemHash(ipath):
    hl = hashlib.sha1()
    with open(ipath,'rb') as f:
        for chunk in iter(lambda: f.read(128*hl.block_size), b''):
             hl.update(chunk)
    return hl.hexdigest()