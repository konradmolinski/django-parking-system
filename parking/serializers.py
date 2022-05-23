from rest_framework import serializers


class UserStorySerializer(serializers.Serializer):
    plate_num = serializers.CharField(max_length=50)
