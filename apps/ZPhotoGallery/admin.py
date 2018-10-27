#__author__ = 'ambler'

from django.contrib import admin


from .models import *

#admin.site.register(Question)

admin.site.register(ZPhotoGallerys, ZPhotoGalleryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ZPGFile, ZPGFileAdmin)