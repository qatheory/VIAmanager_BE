from django.db import models


class Workspace(models.Model):
    createdDate = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=100, blank=False)
    createdBy = models.ForeignKey(
        'auth.User', related_name='workspaces', on_delete=models.CASCADE)

    class Meta:
        ordering = ['createdDate']
