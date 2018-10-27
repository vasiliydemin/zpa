# Generated by Django 2.1.2 on 2018-10-27 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ZPhotoGallery', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ZPGCloudFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.CharField(blank=True, max_length=128, null=True)),
                ('preview', models.CharField(blank=True, max_length=512, null=True)),
                ('path', models.CharField(blank=True, max_length=512, null=True)),
                ('hash', models.CharField(blank=True, max_length=254, null=True)),
                ('minme_type', models.CharField(blank=True, max_length=56, null=True)),
                ('size', models.FloatField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_upd', models.DateTimeField(auto_now=True)),
                ('is_deleted', models.BooleanField(blank=True, default=False)),
                ('is_loaded', models.BooleanField(blank=True, default=False)),
            ],
        ),
    ]
