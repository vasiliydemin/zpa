# Generated by Django 2.1.2 on 2018-10-27 17:12

import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='ZPGFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, max_length=128, null=True)),
                ('image', models.FileField(blank=True, storage=django.core.files.storage.FileSystemStorage(location='/media/sf_E_DRIVE/PHOTO_STORAGE'), upload_to='z')),
                ('size', models.FloatField(blank=True, null=True)),
                ('ext', models.CharField(blank=True, max_length=128, null=True)),
                ('hash', models.CharField(blank=True, max_length=254, null=True)),
                ('camera', models.CharField(blank=True, max_length=128, null=True)),
                ('orig_path', models.TextField(blank=True, null=True)),
                ('width', models.FloatField(blank=True, null=True)),
                ('height', models.FloatField(blank=True, null=True)),
                ('is_movie', models.BooleanField(blank=True, default=True)),
                ('file_date', models.DateTimeField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_upd', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(blank=True, default=False)),
                ('on_cloud', models.BooleanField(blank=True, default=False)),
                ('tags', models.ManyToManyField(blank=True, to='ZPhotoGallery.Tag')),
            ],
        ),
        migrations.CreateModel(
            name='ZPhotoGallerys',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
            ],
        ),
    ]
