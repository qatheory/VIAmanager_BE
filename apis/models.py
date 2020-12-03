from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    label = models.CharField(max_length=100, blank=True)
    group = models.CharField(max_length=255, blank=True, default=1)


class Via(models.Model):
    createdDate = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, default="new Via")
    tfa = models.TextField(blank=True)
    accessToken = models.TextField(blank=True)
    fbid = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=100, blank=True)
    email = models.CharField(max_length=100, blank=True)
    emailPassword = models.CharField(max_length=100, blank=True)
    fbName = models.CharField(
        max_length=100,
        blank=True,
    )
    gender = models.SmallIntegerField(blank=True, null=True)
    dateOfBirth = models.DateTimeField(blank=True, null=True)
    fbLink = models.TextField(blank=True)
    status = models.SmallIntegerField(blank=True, null=True)
    label = models.TextField(blank=True)
    isDeleted = models.BooleanField(default=False)

    # workspace = models.ForeignKey("apis.Workspace",
    #                               related_name="vias",
    #                               on_delete=models.CASCADE)

    class Meta:
        ordering = ["createdDate"]


class Bm(models.Model):
    # createdDate = models.DateTimeField(auto_now_add=True)
    # name = models.CharField(max_length=100, blank=True)
    bmid = models.CharField(max_length=100, blank=True)
    # balance = models.FloatField(blank=True)
    status = models.SmallIntegerField(blank=True, null=True)


class Process(models.Model):
    name = models.CharField(max_length=100, blank=True)
    status = models.SmallIntegerField(blank=True, default=0)


class AutomationLog(models.Model):
    createdDate = models.DateTimeField(auto_now_add=True)
    process = models.CharField(max_length=100, blank=True)
    log = models.TextField(blank=True)
    status = models.CharField(max_length=100, blank=True)
    error = models.CharField(max_length=100, blank=True)
    hide = models.BooleanField(default=False)
