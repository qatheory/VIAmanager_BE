from rest_framework import serializers
from django.contrib.auth.models import User
from apis.models import Workspace, Via

# Via


class ViasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Via
        fields = [
            'id', 'name', 'via_id', 'tfa', 'status', 'createdDate', 'workspace'
        ]


# Workspace
class WorkspaceSerializer(serializers.ModelSerializer):
    vias = serializers.PrimaryKeyRelatedField(many=True,
                                              queryset=Via.objects.all())
    createdBy = serializers.ReadOnlyField(source='createdBy.username')

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'vias', 'createdBy', 'createdDate']


class WorkspaceFullSerializer(serializers.ModelSerializer):
    vias = ViasSerializer(many=True, read_only=True)

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'vias', 'createdBy', 'createdDate']


# User
class UserSerializer(serializers.ModelSerializer):
    workspaces = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Workspace.objects.all())
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', "first_name", "last_name", 'workspaces',
            'password'
        ]

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserFullSerializer(serializers.ModelSerializer):
    workspaces = WorkspaceFullSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            "first_name",
            "last_name",
            'workspaces',
        ]