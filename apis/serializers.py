from rest_framework import serializers
from django.contrib.auth.models import User
from apis.models import Via, Bm, Profile, Process, AutomationLog
from rest_framework_jwt.settings import api_settings
import requests

# Serializers


class ViasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Via
        fields = [
            "id", "name", "tfa", "fbid", "accessToken", "password", "email",
            "emailPassword", "fbName", "dateOfBirth", "gender", "fbLink",
            "status", "label", "isDeleted"
        ]


class BmsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bm
        fields = ["id", "bmid", "status"]


# class WorkspaceSerializer(serializers.ModelSerializer):
#     vias = serializers.PrimaryKeyRelatedField(many=True,
#                                               queryset=Via.objects.all())
#     bms = serializers.PrimaryKeyRelatedField(many=True,
#                                              queryset=BM.objects.all())
#     createdBy = serializers.ReadOnlyField(source="createdBy.username")

#     class Meta:
#         model = Workspace
#         fields = [
#             "id", "name", "accessToken", "vias", "bms", "createdBy",
#             "createdDate"
#         ]

# class WorkspaceId(serializers.ModelSerializer):
#     class Meta:
#         model = Workspace
#         fields = ["id", "name"]

# class WorkspaceUserShort(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ["id", "username"]

# class WorkspaceFullSerializer(serializers.ModelSerializer):
#     vias = ViasSerializer(many=True, read_only=True)
#     createdBy = WorkspaceUserShort(read_only=True)

#     class Meta:
#         model = Workspace
#         fields = [
#             "id", "name", "accessToken", "vias", "bms", "createdBy",
#             "createdDate"
# ]


# User
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["group", "label"]


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()
    profile = ProfileSerializer()

    def get_token(self, object):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(object)
        token = jwt_encode_handler(payload)
        return token

    class Meta:
        model = User
        fields = [
            "id", "username", "token", "first_name", "last_name", "password",
            "profile"
        ]

    def create(self, validated_data):
        profile_data = validated_data.pop("profile")
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data["password"])
        user.save()
        Profile.objects.create(user=user, **profile_data)
        return user


class UserResetPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["password"]

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        return instance


class UserUpdate(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "profile"]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile")
        # Unless the application properly enforces that this field is
        # always set, the following could raise a `DoesNotExist`, which
        # would need to be handled.
        profile = instance.profile

        instance.first_name = validated_data.get("first_name",
                                                 instance.first_name)
        instance.last_name = validated_data.get("last_name",
                                                instance.last_name)
        instance.save()

        profile.label = profile_data.get("label", profile.label)
        profile.group = profile_data.get("group", profile.group)
        profile.save()

        return instance


class UserFullSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["id", "username", "first_name",
                  "last_name",  "profile"]


class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ["id", "name", "status"]


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationLog
        fields = [
            "id", "process", "log", "status", "error", "done"
        ]
