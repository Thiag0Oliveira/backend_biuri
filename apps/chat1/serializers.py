from rest_framework import serializers
from apps.chat1.models import Messages

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Messages
        fields = '__all__'
