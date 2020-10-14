from django.db import models


class Via(models.Model):
    createdDate = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, default="new Via")
    alternativeName = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True)
    status = models.SmallIntegerField(blank=True, default=1)
    password = models.CharField(max_length=100, blank=True)
    label = models.TextField(blank=True)
    tfa = models.TextField(blank=True)
    workspace = models.ForeignKey('apis.Workspace',
                                  related_name='vias',
                                  on_delete=models.CASCADE)

    class Meta:
        ordering = ['createdDate']


class BM(models.Model):
    createdDate = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, default="new Via")
    BMID = models.CharField(max_length=100, blank=True)
    balance = models.FloatField(blank=True)
    status = models.SmallIntegerField(blank=True, default=1)
    workspace = models.ForeignKey('apis.Workspace',
                                  related_name='bms',
                                  on_delete=models.CASCADE)

    class Meta:
        ordering = ['createdDate']


class Workspace(models.Model):
    createdDate = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100,
                            blank=True,
                            default="new Workspace")
    createdBy = models.ForeignKey('auth.User',
                                  related_name='workspaces',
                                  on_delete=models.CASCADE)

    class Meta:
        ordering = ['createdDate']
