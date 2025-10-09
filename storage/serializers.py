from rest_framework import serializers
from .models import UserFile

class UserFileSerializer(serializers.ModelSerializer):
    original_name = serializers.CharField(read_only=True)
    size = serializers.IntegerField(read_only=True)
    upload_date = serializers.DateTimeField(read_only=True)
    last_download = serializers.DateTimeField(read_only=True)

    class Meta:
        model = UserFile
        fields = ('id', 'original_name', 'size', 'upload_date', 'last_download', 'comment', 'unique_identifier')

class UserFileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ('file', 'comment')

class UserFileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFile
        fields = ('comment',)