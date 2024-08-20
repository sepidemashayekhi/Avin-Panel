from rest_framework import serializers
from django.core import validators


class CreateUserSerializer(serializers.Serializer):
    NationalCode = serializers.CharField(required=True)
    Password = serializers.CharField(required=True)



class LoginUserSerializer(serializers.Serializer):
    NationalCode = serializers.CharField(required=True)
    Password = serializers.CharField(required=True)

class RecoverPassSerializer(serializers.Serializer):
    PhoneNumber = serializers.CharField(max_length=14, validators=[
                    validators.RegexValidator(
                        r"^(?:0|98|\+98|\+980|0098|098|00980)?(9\d{9})$",
                                    ("Enter a valid phone number"),
                                    "invalid",
                                ),
                            ],
                             error_messages={
                                 "invalid": ("Enter a valid phone number"),
                             }, allow_null=False)

class SetPassSerializer(serializers.Serializer):
    Key = serializers.CharField(max_length=90, required=True, allow_blank=False, allow_null=False)
    Password = serializers.CharField(max_length=50, required=True, allow_null=False, allow_blank=False)
    Otp = serializers.IntegerField(required=True)