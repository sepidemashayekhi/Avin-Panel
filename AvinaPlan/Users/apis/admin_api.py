from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from Users.models import User, MyTOTPDevice, PassDevice
from Users.serializers import CreateUserSerializer, LoginUserSerializer, RecoverPassSerializer, SetPassSerializer, ActivateUserSerializer, PassUserSerializer
from config import message_error, create_otp, send_sms


import jwt
from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv
load_dotenv()

PATH = os.getenv('PATH')

TOKRNEXP = datetime.now(timezone.utc) + timedelta(hours=5)

class UserPortal(viewsets.ViewSet):

    @action(methods=['post'], detail=False, url_path='create')
    def create_user(self, request):
        data = request.data
        serializer = CreateUserSerializer(data=data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(data['NationalCode'], data['PassWord'])

        if not user:
            return Response(message_error(False, 400, error_code=216), status=status.HTTP_400_BAD_REQUEST)

        return Response(message_error(True, 200, error_code=217), status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='login')
    def login_user(self, request):
        data = request.data
        serializer = LoginUserSerializer(data=data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)

        user = User.objects.check_user_pass(data['NationalCode'], data['PassWord'])
        if not user:
            return Response(message_error(False, 400, error_code=218), status.HTTP_400_BAD_REQUEST)

        token = jwt.encode({'NationalCode': user.NationalCode,
                            'user_id': user.UserId,
                            'exp': TOKRNEXP }, "secret", algorithm="HS256")

        return Response(message_error(True, 200, data=token), status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='recoverpass')
    def recover_pass(self, request):
        data = request.data
        serializer = RecoverPassSerializer(data=data)

        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)

        user = User.objects.filter(PhoneNumber=data['PhoneNumber'],Active=True).first()

        if not user:
            return Response(message_error(False, 400, error_code=209), status.HTTP_400_BAD_REQUEST)

        otp, device = create_otp(user, MyTOTPDevice)
        response = send_sms(otp, data['PhoneNumber'])

        if response != 200:
            return Response(message_error(False, 400, error_code=219), status.HTTP_400_BAD_REQUEST)

        return Response(message_error(True, 200, data={'Key': device.key, 'exp': self.ExTime}), status.HTTP_200_OK)

    @action(methods=['put'], detail=False, url_path='newpass')
    def set_newpass(self, request):
        data = request.data
        serializer = SetPassSerializer(data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208))

        device = MyTOTPDevice.objects.filter(key=data['Key']).first()
        if not device:
            return Response(message_error(True, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        verify = device.verify_token(data['Otp'])

        if not verify:
            return Response(message_error(False, 400, error_code=220), status.HTTP_400_BAD_REQUEST)
        user = device.user
        User.objects.chenge_pass(user, data['Password'])

        return Response(message_error(True, 200, error_code=200), status.HTTP_200_OK)

    @action(methods=['put'], detail=False, url_path='setpass/(?P<key>[^/.]+)')
    def set_pass(self, request, key):
        data = request.data
        serializer = PassUserSerializer(data=data)
        if not isinstance(key, str):
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)

        device = PassDevice.objects.filter(key=key).first()
        user = device.user
        user.Password = data['Password']
        user.save()
        return Response(message_error(True, 200, error_code=200), status.HTTP_200_OK)


class AdminPortal(viewsets.ViewSet):

    @action(methods=['put'], detail=False, url_path='activate')
    def activate_user(self, request):
        data = request.data
        serializer = ActivateUserSerializer(data=data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        user = User.objects.activate_user(data['UserId'])
        if not user:
            return Response(message_error(False, 400, error_code=221), status.HTTP_400_BAD_REQUEST)

        device = PassDevice.objects.create(user=user)
        device.save()
        path = os.path.join(PATH, 'user', 'setpass', device.key)
        response = send_sms(path, user.PhoneNumber)
        if response != 200:
            return Response(message_error(False, 400, error_code=222), status.HTTP_400_BAD_REQUEST)
        return Response(message_error(True, 200, error_code=200), status.HTTP_200_OK)







