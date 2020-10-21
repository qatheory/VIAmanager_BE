from rest_framework import serializers
from django.contrib.auth.models import User
from apis.models import Via, BM
from rest_framework_jwt.settings import api_settings
import requests

# Serializers


class ViasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Via
        fields = [
            'id', 'name', 'tfa', 'fbid', 'accessToken', 'password', 'email',
            'emailPassword', 'fbName', 'dateOfBirth', 'gender', 'fbLink',
            'status', 'label'
        ]


class BMsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BM
        fields = ['id', 'name', 'accessToken', 'appID', 'createdDate']


# class WorkspaceSerializer(serializers.ModelSerializer):
#     vias = serializers.PrimaryKeyRelatedField(many=True,
#                                               queryset=Via.objects.all())
#     bms = serializers.PrimaryKeyRelatedField(many=True,
#                                              queryset=BM.objects.all())
#     createdBy = serializers.ReadOnlyField(source='createdBy.username')

#     class Meta:
#         model = Workspace
#         fields = [
#             'id', 'name', 'accessToken', 'vias', 'bms', 'createdBy',
#             'createdDate'
#         ]

# class WorkspaceId(serializers.ModelSerializer):
#     class Meta:
#         model = Workspace
#         fields = ['id', 'name']

# class WorkspaceUserShort(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'username']

# class WorkspaceFullSerializer(serializers.ModelSerializer):
#     vias = ViasSerializer(many=True, read_only=True)
#     createdBy = WorkspaceUserShort(read_only=True)

#     class Meta:
#         model = Workspace
#         fields = [
#             'id', 'name', 'accessToken', 'vias', 'bms', 'createdBy',
#             'createdDate'
# ]


# User
class UserSerializer(serializers.ModelSerializer):
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
            'id', 'username', 'token', "first_name", "last_name", 'password'
        ]

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdate(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class UserFullSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            "first_name",
            "last_name",
        ]
