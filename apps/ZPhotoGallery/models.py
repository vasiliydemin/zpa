#__author__ = 'ambler'

from django.db import models
from django.contrib import admin
from django.core.files.storage import FileSystemStorage
from django.db.models.signals import post_save, pre_delete
from django.dispatch.dispatcher import receiver
from django.contrib.admin import DateFieldListFilter

from django.conf import settings


fs = FileSystemStorage(location=settings.ZPG_DATA_STORAGE)


class ZPhotoGallerys(models.Model):
    title = models.CharField(max_length=60)
    def __str__(self):
        return self.title

class Tag(models.Model):
    tag = models.CharField(max_length=254)
    def __str__(self):
        return self.tag

class ZPGFile(models.Model):

    filename = models.CharField(max_length=128, blank=True, null=True)
    image = models.FileField(upload_to = 'z', storage = fs, blank=True)

    size = models.FloatField(blank=True, null=True)
    ext = models.CharField(max_length=128, blank=True, null=True)
    hash = models.CharField(max_length=254, blank=True, null=True)
    camera = models.CharField(max_length=128, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    orig_path = models.TextField(blank=True, null=True)

    width = models.FloatField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    is_movie = models.BooleanField(blank=True, default=True)


    file_date = models.DateTimeField(blank=True, null=True)
    #exif_date = models.DateTimeField(blank=True, null=True)
    #path_date = models.DateTimeField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    last_upd = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(blank=True, default=False)
    on_cloud = models.BooleanField(blank=True, default=False)


    thumb_sizes={'thumb':(250, 250),
                 'normal':(1024, 1024)}

    def is_image(self):
        return not self.is_movie

    def is_video(self):
        return self.is_movie

    def is_video(self):
        return not self.is_image

    def image_img(self):
        if self.image and self.image.storage.exists('thumb/%s' % (self.image.url)):
            return u'<img style="width: 150px; height: 150px" src="/static/thumb/%s" />' % self.image.url
        else:
            return 'zzz'

    image_img.short_description = 'preview'
    image_img.allow_tags = True

    def __str__(self):
        return self.filename or self.image.name

    def thumb(self):
            url=self.image.url
            thumbs={}
            for sizes in self.thumb_sizes:
                  thumbs[sizes]= '%s/%s' % (sizes, url)
            return thumbs


@receiver(pre_delete, sender=ZPGFile)
def _delete_th(sender, instance, **kwargs):
    if instance.image:
        storage, path = instance.image.storage, instance.image.path
        storage.delete(path)




class ZPhotoGalleryAdmin(admin.ModelAdmin):
    pass

class TagAdmin(admin.ModelAdmin):
    list_display = ["tag"]

class ZPGFileAdmin(admin.ModelAdmin):
#    search_fields = ["ext"]
    list_display = ["image_img", "__str__", "ext", "size", "camera", "file_date", "created"]
    list_filter = [('file_date', DateFieldListFilter), "tags", "ext", "camera"]




#class FolderForm(ModelForm):
#
#      class Meta:
#            model = Folder