# Generated by Django 3.1.1 on 2020-10-15 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0003_bm'),
    ]

    operations = [
        migrations.AddField(
            model_name='workspace',
            name='accessToken',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='workspace',
            name='appID',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]