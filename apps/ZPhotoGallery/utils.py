# -*- coding: utf-8 -*-
__author__ = 'ambler'




import os
from PIL import Image
from PIL.ExifTags import TAGS
import sqlite3
from datetime import date
import os.path, time, datetime
import re
import shutil
import hashlib
import requests
#import pyexiv2


from .models import *

import subprocess, re







def getCloudRidData(path='', cli=None, dir_import=''):

    save_path = "%s/%s" % (dir_import, 'CLOUD')
    lpath = [g for g in path.split('/') if g and g!='disk:']
    print('lp: ', lpath)
    if len(lpath)>1:
        save_path = "%s/%s" % (save_path, '/'.join(lpath[1:]))

    if not os.path.exists(save_path):
        os.makedirs(save_path)

    print ('sp: ', save_path)

    for i in cli.get_content_of_folder(path).get_children():
        if i.type=='file':
            print(i.type, i.name, i.path)
            fname = "%s/%s" % (save_path, i.name)
            if os.path.exists(fname):
                print('CLOUD FILE IMPORTED')
            else:
                ur=cli.get_download_link_to_file(i.path)
                r = requests.get(ur['href'], stream=True)
                if r.status_code == 200:
                    with open(fname, 'wb') as f:
                        r.raw.decode_content = True
                        shutil.copyfileobj(r.raw, f)
                del r
                #cli.unpublish_folder_or_file(i.path)
        else:
            getCloudRidData(i.path, cli, dir_import)





def getItemSize(pathtovideo):
    pt_dim = re.compile(r'Stream.*Video.* ([0-9]+)x([0-9]*)')
    pt_isv = re.compile(r'Duration: 00:00:00')

    p = subprocess.Popen(['ffmpeg', '-i', pathtovideo],
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


#print get_size('/home/ambler/PyProjects/ambler/videoc/2.jpg')
#print get_size('/home/ambler/PyProjects/ambler/videoc/1.MP4')


def getExif(file=''):

    exif = {}
    try:
        img = Image.open(file)

        try:
            exif_data = img._getexif()
        except:
            exif_data = None


        if exif_data:
            for k,v in img._getexif().items():
                if TAGS.get(k, None):
                    exif[TAGS[k]] =  v
    except:
        pass
    return exif


def copyFile(file_src, file_dest):
    f1 = open(file_src,'rb')
    f2 = open(file_dest,'wb')

    with open(file_src,'rb') as f:
        for chunk in iter(lambda: f.read(128*1024), b''):
             f2.write(chunk)

    f2.close()

    return 1



def getItemHash(ipath=''):
    hl = hashlib.sha1()
    with open(ipath,'rb') as f:
        for chunk in iter(lambda: f.read(128*hl.block_size), b''):
             hl.update(chunk)
    return hl.hexdigest()

def getCameraFromExif(file='', exif={}):
    camera = ''
    if exif.keys():
        camera = "%s-%s" % (exif.get('Make', 'camera'), exif.get('Model', 'xz'))
        camera = camera #.decode('utf-8')

        camera = camera.replace('\x00','')
        camera = re.sub(' +',' ',camera)

    return camera

def getDTfromFile(file = ''):
    dt = None
    ltime = os.path.getmtime(file)
    dt = datetime.datetime.fromtimestamp(ltime)
    return dt

def getDTfromExif(file = '', exif={}):

    dt = None
    if exif.keys():

        dt = exif.get('DateTimeDigitized', exif.get('DateTimeOriginal', exif.get('DateTime', '')))
        if dt != '0000:00:00 00:00:00':
            try:
                dt = datetime.datetime.strptime(dt, '%Y:%m:%d %H:%M:%S')
            except:
                dt = None
        else:
            dt = None

    return dt

def getDTfromPath(path=''):

    re1= re.compile(r'(\d{2})[\.\:\-\/](\d{4})')
    re2= re.compile(r'(\d{4})[\.\:\-\/](\d{2})')
    re3= re.compile(r'(.*)(\d{4}).*')

    gg = path.split('/')
    gg.reverse()

    dt =  {'m':1, 'y':1900, 'd':1}

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


def copyFileToStorage(data = {}, istorage = ''):

    thumb_sizes={'thumb':(250, 250),
                 'normal':(1280, 1280)}

    new_size = 0

    try:
    #if data['ext'] == 'JPG':
        pyear = os.path.join(istorage, data['image'].split('/')[0])
        pmonth = os.path.join(pyear, data['image'].split('/')[1])

        pfile = os.path.join(istorage, data['image'])

        if not os.path.exists(pyear):
            os.makedirs(pyear)

        if not os.path.exists(pmonth):
            os.makedirs(pmonth)

        data['orig_path'] = data['orig_path'] #unicode(data['orig_path'])

        #shutil.copy2(data['orig_path'], pfile)
        print (data['orig_path'], pfile)
        copyFile(data['orig_path'], pfile)

        isimg = 0
        try:
            z=Image.open(pfile)
            isimg = 1
        except:
            pass

        if '.THM' in pfile:
            isimg = 0



        if isimg:
            z=Image.open(pfile)
            for orientation in TAGS.keys():
                if TAGS[orientation]=='Orientation': break

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
                    #print new_size

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
                th_pyear = os.path.join(th_p, data['image'].split('/')[0])
                th_pmonth = os.path.join(th_pyear, data['image'].split('/')[1])
                th_pfile = os.path.join(istorage, thms, data['image'])

                if not os.path.exists(th_p):
                    os.makedirs(th_p)

                if not os.path.exists(th_pyear):
                    os.makedirs(th_pyear)

                if not os.path.exists(th_pmonth):
                    os.makedirs(th_pmonth)

                try:
                    if not data['is_img']:

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

    #else:
    except:
        return (0, new_size)

    return (1, new_size)


def getKWfromPath(path= '', fdir =''):

    rkw=[]

    stopw = ['CLOUD', 'новая', 'печ', 'тел', 'телефон', 'телефон2' , 'Фигня', 'флешка', 'Фотки', 'фото', 'Фото', 'digimax', 'fignay', 'new', 'new2', 'other', 'print', 'telefon', 'vid', 'vsyakoe', 'всякое', 'к', 'На отправку', 'на печать', '103d5000', '101anv01', '.picasaoriginals','fromdisks', 'fromdisks2', 'foto', 'fotos_1']+[str(i) for i in range(0, 50)]+['foto_'+str(i) for i in range(0, 50)]

    kw = []

    kw =  [z.lower() for z in path.replace(fdir, '').split('/')[:-1] if z and z.lower() not in stopw]

    for k in kw:
        k = k.replace('\'','')
        tg = Tag.objects.filter(tag=k)
        if tg:
            rkw.append(tg[0])
        else:
            tg = Tag.objects.create(tag=k)
            rkw.append(tg)
    return rkw

def scanImportFolder(i_dir='', result=[], dir_storage='', dir_import=''):
    imported_cnt=0
    print (i_dir)
    for id_item in os.listdir(i_dir):
        ItemPath = os.path.join(i_dir, id_item)
        print (ItemPath)

        if os.path.isdir(ItemPath) == True:
            result = scanImportFolder(ItemPath, result, dir_storage, dir_import)
        else:


            itemHash = getItemHash(ItemPath)
            #print ItemPath, itemHash
            #copyFile(ItemPath, '%s/%s' % (dir_storage, id_item))

            z=ZPGFile.objects.filter(hash = itemHash)
            if z:
                print ('exists')


            else:
                data = {}
                exif = getExif(ItemPath)
                #print (exif)



                zfile = ZPGFile()
                #TODO проблема с датами
                #print [getDTfromExif(ItemPath, exif), getDTfromFile(ItemPath), getDTfromPath(ItemPath)]
                date = [d for d in [getDTfromExif(ItemPath, exif), getDTfromFile(ItemPath), getDTfromPath(ItemPath)] if d]
                if date:
                    zfile.file_date = data['date'] = date[0]

                #print zfile.file_date

                zfile.ext = id_item.split('.')[-1]

                zfile.filename = data['filename']= '%s%s.%s' % (zfile.file_date.strftime('%Y%m%d%H%M%S'), str(time.time())[6:].replace('.', ''), zfile.ext)
                data['image']= '%s/%s' % (zfile.file_date.strftime('%Y/%m'), data['filename'])
                zfile.orig_path = data['orig_path'] = ItemPath #.decode('utf-8')

                #image = models.FileField(upload_to = 'z', storage = fs)
                #data['path']=ItemPath #.decode('utf-8')

                zfile.size=os.path.getsize(ItemPath)

                zfile.hash = itemHash #getItemHash(ItemPath)
                zfile.camera=getCameraFromExif(ItemPath, exif)
                zfile.image.name = data['image']

                hw_isv = getItemSize(ItemPath)

                zfile.width, zfile.height = hw_isv[0]
                if hw_isv[0]!=(0,0):
                    zfile.is_movie = hw_isv[1]
                else:
                    zfile.is_movie = 0

                data['is_img'] = zfile.is_movie

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


            #result.append(1)


    return imported_cnt





