from rest_framework import serializers
from snippets.models import Snippet, LANGUAGE_CHOICES, STYLE_CHOICES
from django.contrib.auth.models import User
from workspaces.models import Workspace


class UserSerializer(serializers.ModelSerializer):
    workspaces = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Workspace.objects.all())
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', "first_name",
                  "last_name", 'workspaces', 'password']

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user
