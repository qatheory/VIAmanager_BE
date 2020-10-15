# Generated by Django 3.1.2 on 2020-10-14 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='via',
            name='via_id',
        ),
        migrations.AddField(
            model_name='via',
            name='alternativeName',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='via',
            name='email',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='via',
            name='label',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='via',
            name='password',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='via',
            name='status',
            field=models.SmallIntegerField(blank=True, default=1),
        ),
        migrations.AlterField(
            model_name='via',
            name='tfa',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='workspace',
            name='name',
            field=models.CharField(blank=True, default='new Workspace', max_length=100),
        ),
    ]