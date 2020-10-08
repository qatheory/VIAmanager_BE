from django.db import models


class Via(models.Model):
    createdDate = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=True, default="new Via")
    via_id = models.CharField(max_length=100, blank=False)
    status = models.SmallIntegerField()
    tfa = models.TextField()
    workspace = models.ForeignKey('apis.Workspace',
                                  related_name='vias',
                                  on_delete=models.CASCADE)

    class Meta:
        ordering = ['createdDate']


class Workspace(models.Model):
    createdDate = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=False)
    createdBy = models.ForeignKey('auth.User',
                                  related_name='workspaces',
                                  on_delete=models.CASCADE)

    class Meta:
        ordering = ['createdDate']