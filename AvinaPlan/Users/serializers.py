from rest_framework import serializers
from django.core import validators
from Users.models import User


class CreateUserSerializer(serializers.Serializer):
    FullName = serializers.CharField(required=True, max_length=150)
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
    NationalCode = serializers.CharField(required=True, max_length=50)

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

class ActivateUserSerializer(serializers.Serializer):
    UserId = serializers.CharField(max_length=50, required=True, allow_blank=False, allow_null=False)
    Accept = serializers.BooleanField(required=True)

class PassUserSerializer(serializers.Serializer):
    Password = serializers.CharField(max_length=50, required=True, allow_null=False, allow_blank=False)

class UserDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['UserId', 'FullName', 'NationalCode', 'PhoneNumber']


class UserWriteDetailSerializer(serializers.Serializer):
    UserId = serializers.CharField(max_length=150, required=True, allow_null=False, allow_blank=False)
    FullName = serializers.CharField(max_length=150, required=False, allow_null=True)
    NationalCode = serializers.CharField(max_length=150, required=False, allow_null=True)
    PhoneNumber = serializers.CharField(max_length=150, required=False, allow_null=True)

class UserDelete(serializers.Serializer):
    UserId = serializers.CharField(max_length=50, required=True, allow_blank=False, allow_null=False)