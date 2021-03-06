# Generated by Django 3.1.1 on 2020-10-29 11:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Bm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdDate', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, default='new Via', max_length=100)),
                ('BmID', models.CharField(blank=True, max_length=100)),
                ('balance', models.FloatField(blank=True)),
                ('status', models.SmallIntegerField(blank=True, default=1)),
            ],
            options={
                'ordering': ['createdDate'],
            },
        ),
        migrations.CreateModel(
            name='Via',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('createdDate', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(blank=True, default='new Via', max_length=100)),
                ('tfa', models.TextField(blank=True)),
                ('accessToken', models.TextField(blank=True)),
                ('fbid', models.CharField(blank=True, max_length=100)),
                ('password', models.CharField(blank=True, max_length=100)),
                ('email', models.CharField(blank=True, max_length=100)),
                ('emailPassword', models.CharField(blank=True, max_length=100)),
                ('fbName', models.CharField(blank=True, max_length=100)),
                ('gender', models.SmallIntegerField(blank=True, null=True)),
                ('dateOfBirth', models.DateTimeField(blank=True, null=True)),
                ('fbLink', models.TextField(blank=True)),
                ('status', models.SmallIntegerField(blank=True, default=1)),
                ('label', models.TextField(blank=True)),
                ('isDeleted', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['createdDate'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(blank=True, max_length=100)),
                ('group', models.CharField(blank=True, default=1, max_length=255)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
