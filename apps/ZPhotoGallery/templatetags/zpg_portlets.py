from django import template
#from djamper_cms.utils import *
from django.contrib.auth.models import User
from apps.ZPhotoGallery.models import *
from django.db import connection



register = template.Library()



@register.inclusion_tag('ZPhotoGallery/portlet_photonavi.html', takes_context=True)
def portlet_photonavi(context):

    cursor = connection.cursor()

    cursor.execute("select min(file_date), max(file_date) from ZPhotoGallery_zpgfile")

    row = cursor.fetchone()
    cursor.close()
    return {'years': range(int(row[0][:4]), int(row[1][:4]) + 1), 'months': ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']}

