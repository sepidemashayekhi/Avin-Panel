from rest_framework import serializers



class CreateUserSerializer(serializers.Serializer):
    NationalCode = serializers.CharField(required=True)
    Password = serializers.CharField(required=True)
