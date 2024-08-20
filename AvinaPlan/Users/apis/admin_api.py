from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django_otp.oath import TOTP

from Users.models import User, MyTOTPDevice
from Users.serializers import CreateUserSerializer, LoginUserSerializer, RecoverPassSerializer, SetPassSerializer
from config import message_error

import jwt
from datetime import timedelta, datetime, timezone
import requests
import os
from dotenv import load_dotenv

load_dotenv()

PHONNUMBER = os.getenv('PhoneNumber')
ACCESSHASH = os.getenv('AccessHash')
PATTERNID = os.getenv('PatternId')
URL = os.getenv('URL')

TOKRNEXP = datetime.now(timezone.utc) + timedelta(hours=5)

class UserPortal(viewsets.ViewSet):
    ExTime = 120
    def _send_sms(self, message, phone_number):
        params = {
            'AccessHash': ACCESSHASH,
            'PhoneNumber': PHONNUMBER,
            'PatternId': PATTERNID,
            'RecNumber': phone_number,
            'Smsclass': 1,
            'token1': message
        }
        try:
            response = requests.get(url=URL, params=params)
        except:
            return 500
        return response.status_code

    def _create_otp(self, user):
        device = MyTOTPDevice.objects.create(user=user, step=self.ExTime)
        device.save()
        totp = TOTP(key=device.bin_key, step=self.ExTime)
        token = totp.token()
        return token, device

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

    @action(methods=['put'], detail=False, url_path='activete')
    def activate_user(self, request):
        pass

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

        otp, device = self._create_otp(user)
        response = self._send_sms(otp, data['PhoneNumber'])

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
            pass

