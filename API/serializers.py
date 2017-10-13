from rest_framework import serializers
from API.models import Alert

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = ('timestamp', 'type', 'condition','alert')
