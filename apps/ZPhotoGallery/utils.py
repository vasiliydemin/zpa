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
from local_settings import *


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

    for cloit in ZPGCloudFile.objects.filter(is_loaded=False, path__startswith='disk:/Фотокамера (deminvlad09)')[:10]:
        print(cloit.filename)
        save_cloud_file(cloit, cli, dir_import)


def import_to_zpa(dir_storage, dir_import):

    for item in os.listdir(dir_import):
        item_path = os.path.join(dir_import, item)
        print (item_path)

        if os.path.isdir(item_path) == True:
            import_to_zpa(dir_storage, item_path)
        else:
            item_hash = getItemHash(item_path)

            if not ZPGFile.objects.filter(hash=item_hash) or 1:
                zfile = ZPGFile()

                exif = get_exif_data(item_path)
                zfile.file_date = get_datetime_from_exif(item_path, exif) or get_datetime_from_path(item_path) or get_datetime_from_file(item_path)
                zfile.ext = item.split('.')[-1]
                zfile.filename = '%s%s.%s' % (zfile.file_date.strftime('%Y%m%d%H%M%S'), str(time.time())[6:].replace('.', ''), zfile.ext)
                zfile.orig_path = item_path
                zfile.size=os.path.getsize(item_path)
                zfile.hash = item_hash
                zfile.camera=get_camera_from_exif(exif)
                zfile.image.name = '%s/%s' % (zfile.file_date.strftime('%Y/%m'), zfile.filename)

                hw_isv = get_media_size(item_path)
                zfile.width, zfile.height = hw_isv[0]
                if hw_isv[0]!=(0,0):
                    zfile.is_movie = hw_isv[1]
                else:
                    zfile.is_movie = 0

                savedfile = copy_file_to_storage(zfile, dir_storage)

                if savedfile[0]:
                    if savedfile[1]:
                        zfile.width, zfile.height = zfile.height, zfile.width
                    zfile.save()
                    print ('saved')
                    for kw in get_kw_from_path(item_path, dir_import):
                        zfile.tags.add(kw)
                    zfile.save()

                else:
                    print ('no save')
                    del zfile
            else:
                print('exists')


def get_kw_from_path(path, fdir):
    rkw=[]

    stopw = ['CLOUD', 'новая', 'печ', 'тел', 'телефон', 'телефон2' , 'Фигня', 'флешка', 'Фотки', 'фото', 'Фото', 'digimax', 'fignay', 'new', 'new2', 'other', 'print', 'telefon', 'vid', 'vsyakoe', 'всякое', 'к', 'На отправку', 'на печать', '103d5000', '101anv01', '.picasaoriginals','fromdisks', 'fromdisks2', 'foto', 'fotos_1']+[str(i) for i in range(0, 50)]+['foto_'+str(i) for i in range(0, 50)]

    kw = [z.lower() for z in path.replace(fdir, '').split('/')[:-1] if z and z.lower() not in stopw]

    for k in kw:
        k = k.replace('\'','')
        tg = Tag.objects.filter(tag=k)
        if tg:
            rkw.append(tg[0])
        else:
            tg = Tag.objects.create(tag=k)
            rkw.append(tg)
    return rkw


def copy_file_to_storage(zpgfile, istorage):

    thumb_sizes={'thumb':(250, 250),
                 'normal':(1280, 1280)}

    new_size = 0

    try:
        pyear = os.path.join(istorage, zpgfile.image.name.split('/')[0])
        pmonth = os.path.join(pyear, zpgfile.image.name.split('/')[1])
        pfile = os.path.join(istorage, zpgfile.image.name)

        if not os.path.exists(pyear):
            os.makedirs(pyear)

        if not os.path.exists(pmonth):
            os.makedirs(pmonth)

        print (zpgfile.orig_path, pfile)
        shutil.copy2(zpgfile.orig_path, pfile)

        isimg = 0
        try:
            Image.open(pfile)
            isimg = 1
        except:
            pass

        if '.THM' in pfile:
            isimg = 0

        if isimg:
            z=Image.open(pfile)
            for orientation in TAGS.keys():
                if TAGS[orientation] == 'Orientation': break

            if '_getexif' in dir(z):
                fex = z._getexif()
            else:
                fex = None
            if fex:
                exif=dict(z._getexif().items())

                if exif.get(orientation,'*') != '*':
                    if exif[orientation] == 3 :
                        z=z.rotate(180, expand=True)
                    elif exif[orientation] == 6 :
                        z=z.rotate(270, expand=True)
                        new_size=1
                    elif exif[orientation] == 8 :
                        z=z.rotate(90, expand=True)
                        new_size=1
                    z.save(pfile, quality = 100)

                    #TODO: здесь какой-то косяк происходит, не копируются exif данные
                    #/mnt/drive_d/PHOTO_IMPORT/Анина свадьба 13.07.13/IMG_1785.JPG /mnt/drive_d/PHOTO_STORAGE/2013/07/20130712104615862913.JPG
                    #try:
                    #    oldmeta = pyexiv2.ImageMetadata(data['orig_path'])
                    #    oldmeta.read()
                    #
                    #    newmeta = pyexiv2.ImageMetadata(pfile)
                    #    newmeta.read()

                    #    oldmeta.copy(newmeta)
                    #    new_size = z.size
                    #    newmeta['Exif.Image.Orientation'] = 1
                    #    newmeta["Exif.Photo.PixelXDimension"] = z.size[0]
                    #    newmeta["Exif.Photo.PixelYDimension"] = z.size[1]

                    #    newmeta.write()
                    #except:
                    #    print 'ZZZ: meta bag'

            for thms in thumb_sizes.keys():
                th_p = os.path.join(istorage, thms)
                th_pyear = os.path.join(th_p, zpgfile.image.name.split('/')[0])
                th_pmonth = os.path.join(th_pyear, zpgfile.image.name.split('/')[1])
                th_pfile = os.path.join(istorage, thms, zpgfile.image.name)

                if not os.path.exists(th_p):
                    os.makedirs(th_p)

                if not os.path.exists(th_pyear):
                    os.makedirs(th_pyear)

                if not os.path.exists(th_pmonth):
                    os.makedirs(th_pmonth)

                try:
                    if not zpgfile.is_movie:

                        z=Image.open(pfile)

                        if thms == 'thumb':
                            width, height = z.size
                            if width > height:
                                delta = width - height
                                left = int(delta/2)
                                upper = 0
                                right = height + left
                                lower = height
                            else:
                               delta = height - width
                               left = 0
                               upper = int(delta/2)
                               right = width
                               lower = width + upper

                            z = z.crop((left, upper, right, lower))

                        z.thumbnail(thumb_sizes[thms], Image.ANTIALIAS)
                        z.save(th_pfile, quality = 75)
                except:
                    pass
        else:
            pass
    except:
        return (0, new_size)

    return (1, new_size)


def get_media_size(path):
    pt_dim = re.compile(r'Stream.*Video.* ([0-9]+)x([0-9]*)')
    pt_isv = re.compile(r'Duration: 00:00:00')

    p = subprocess.Popen([ffmpeg_path, '-i', path],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()
    stderr = stderr.decode("utf-8")
    match, match_v = pt_dim.search(stderr), pt_isv.search(stderr)
    x = y = z = 0

    if match:
        x, y = map(int, match.groups()[0:2])

    if not match_v:
        z=1

    return (x, y), z


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
    #TODO: сделать нормальный поиск даты в пути
    re1= re.compile(r'(\d{2})[\.\:\-\/](\d{4})')
    re2= re.compile(r'(\d{4})[\.\:\-\/](\d{2})')
    re3= re.compile(r'(.*)(\d{4}).*')
    gg = path.split(os.path.sep)
    gg.reverse()
    dt = {'m':1, 'y':1900, 'd':1}

    for pf in gg:
        ptt = re1.findall(pf)
        if ptt:
            dt['m'] = ptt[0][0]
            dt['y'] = ptt[0][1]
            break

        ptt = re2.findall(pf)
        if ptt:
            dt['m'] = ptt[0][1]
            dt['y'] = ptt[0][0]
            break

        ptt = re3.findall(pf)
        if ptt:
            dt['y'] = ptt[0][1]
            break

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