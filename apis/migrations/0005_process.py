# Generated by Django 3.1.1 on 2020-11-26 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0004_auto_20201120_1152'),
    ]

    operations = [
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('status', models.SmallIntegerField(blank=True, default=0)),
            ],
        ),
    ]
