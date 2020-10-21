from django.db import models


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
    status = models.SmallIntegerField(blank=True, default=1)
    label = models.TextField(blank=True)

    # workspace = models.ForeignKey('apis.Workspace',
    #                               related_name='vias',
    #                               on_delete=models.CASCADE)

    class Meta:
        ordering = ['createdDate']


class BM(models.Model):
    createdDate = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, default="new Via")
    BMID = models.CharField(max_length=100, blank=True)
    balance = models.FloatField(blank=True)
    status = models.SmallIntegerField(blank=True, default=1)

    # workspace = models.ForeignKey('apis.Workspace',
    #                               related_name='bms',
    #                               on_delete=models.CASCADE)

    class Meta:
        ordering = ['createdDate']


# class Workspace(models.Model):
#     createdDate = models.DateTimeField(auto_now_add=True)
#     name = models.CharField(max_length=100,
#                             blank=True,
#                             default="new Workspace")
#     accessToken = models.CharField(max_length=200,
#                                    blank=True,
#                                    )
#     createdBy = models.ForeignKey('auth.User',
#                                   related_name='workspaces',
#                                   on_delete=models.CASCADE)

#     class Meta:
#         ordering = ['createdDate']
