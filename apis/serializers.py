from rest_framework import serializers
from django.contrib.auth.models import User
from apis.models import Workspace, Via
from rest_framework_jwt.settings import api_settings
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


class WorkspaceUserShort(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class WorkspaceFullSerializer(serializers.ModelSerializer):
    vias = ViasSerializer(many=True, read_only=True)
    createdBy = WorkspaceUserShort(read_only=True)

    class Meta:
        model = Workspace
        fields = ['id', 'name', 'vias', 'createdBy', 'createdDate']


# User
class UserSerializer(serializers.ModelSerializer):
    workspaces = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Workspace.objects.all())
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    def get_token(self, object):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(object)
        token = jwt_encode_handler(payload)
        return token

    class Meta:
        model = User
        fields = [
            'id', 'username', 'token', "first_name", "last_name", 'workspaces',
            'password'
        ]

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdate(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "first_name", "last_name"
        ]


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
