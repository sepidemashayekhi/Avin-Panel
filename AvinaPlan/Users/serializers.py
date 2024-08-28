from rest_framework import serializers
from django.core import validators
from Users.models import User, Menu, Flag, UserAccess, Access


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

class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = ['Title', 'Priority']

class MenuSerializer(serializers.ModelSerializer):

    FlagId = FlagSerializer()
    class Meta:
        model = Menu
        fields = '__all__'

class UserAccessSerializer(serializers.Serializer):
    UserId = serializers.CharField()  # Assuming the custom field is a CharField
    MenuId = serializers.CharField()
    AccessId = serializers.CharField()

    class Meta:
        model = UserAccess
        fields = ['UserId', 'MenuId', 'AccessId']

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)

        try:
            user = User.objects.get(UserId=internal_data['UserId'])
            menu = Menu.objects.get(MenuId=internal_data['MenuId'])
            access = Access.objects.get(AccessId=internal_data['AccessId'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"UserId": "User not found"})
        except Menu.DoesNotExist:
            raise serializers.ValidationError({"MenuId": "Menu not found"})
        except Access.DoesNotExist:
            raise serializers.ValidationError({"AccessId": "Access not found"})

        internal_data['UserId'] = user
        internal_data['MenuId'] = menu
        internal_data['AccessId'] = access

        return internal_data

    def create(self, validated_data):
        # for item in validated_data:
        user_access = UserAccess.objects.create(
            UserId=validated_data['UserId'],
            MenuId=validated_data['MenuId'],
            AccessId=validated_data['AccessId'],
        )
        return user_access

