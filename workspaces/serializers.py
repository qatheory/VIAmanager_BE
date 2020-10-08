from rest_framework import serializers
from workspaces.models import Workspace
from vias.models import Via


class WorkspaceSerializer(serializers.ModelSerializer):
    vias = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Via.objects.all())
    createdBy = serializers.ReadOnlyField(source='createdBy.username')

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'vias', 'createdBy', 'createdDate']
