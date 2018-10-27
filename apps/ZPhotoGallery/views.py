__author__ = 'ambler'

from django.http import HttpResponse
from django.shortcuts import render
from django.template import Context, loader
from apps.ZPhotoGallery.models import *
#from django.utils import  #simplejson
import json as simplejson


def base_view(request):

    c = {}

    return render(request, 'ZPhotoGallery/hmgview.html', c)



def getPhotos(request):

    c = {}
    _get = request.GET

    b_start = int(_get.get('b_start', 0))
    b_end = int(_get.get('b_end', 9))

    if int(_get['month']) and int(_get['year']):
        z=ZPGFile.objects.filter(file_date__year=int(_get['year']), file_date__month=int(_get['month']), is_movie=0).order_by('-file_date')[b_start:b_end]
    elif int(_get['year']):
        z=ZPGFile.objects.filter(file_date__year=int(_get['year']), is_movie=0).order_by('-file_date')[b_start:b_end]
    else:
        z=ZPGFile.objects.filter(is_movie=0).order_by('-file_date')[b_start:b_end]
    c['files'] = z


    return render(request, 'ZPhotoGallery/photos_view.html', c)



def ajax_query(request):

    _get = request.GET

    if _get.get('query', '')=='getImageDetails':
        if _get.get('item_id', ''):
            item = ZPGFile.objects.get(id = _get.get('item_id', ''))

            zdata = [{'image_url':'/static/normal/%s' % item.image.url,
                      'width':item.width,
                      'height':item.height,
                      'date':item.file_date.strftime("%d.%m.%Y %H:%M:%S"),
                      'camera':item.camera or '',
                      'filepath':item.orig_path or ''}]




    if _get.get('query', '')=='dates_list':
        if _get.get('m_year', 0) and _get.get('m_month', 0):
            dates = [z.day for z in ZPGFile.objects.filter(file_date__year=_get.get('m_year', 0), file_date__month=_get.get('m_month', 0)).dates('file_date','day')]
        elif _get.get('m_year', 0):
            dates = [z.month for z in ZPGFile.objects.filter(file_date__year=_get.get('m_year', 0)).dates('file_date','month')]
        else:
            dates = [z.year for z in ZPGFile.objects.dates('file_date','year')]


        zdata = [{'val':z, 'name':z} for z in dates]
        zdata.reverse()

    data = simplejson.dumps(zdata)
    print(data)

    return HttpResponse(data) #, mimetype='application/json')