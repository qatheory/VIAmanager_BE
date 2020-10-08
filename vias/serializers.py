from rest_framework import serializers
from vias.models import Via


class ViasSerializer(serializers.ModelSerializer):

    class Meta:
        model = Via
        fields = ['id', 'name', 'via_id', 'tfa',
                  'status', 'createdDate', 'workspace']
