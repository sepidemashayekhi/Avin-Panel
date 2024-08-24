from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from django.urls import reverse
from django.contrib.auth.hashers import make_password

from Users.models import User, MyTOTPDevice, PassDevice
from Users.serializers import (CreateUserSerializer, LoginUserSerializer, RecoverPassSerializer, SetPassSerializer, ActivateUserSerializer, PassUserSerializer,
                               UserDetailSerializer, UserWriteDetailSerializer, UserDelete
                               )
from config import message_error, create_otp, send_sms


import jwt
from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

load_dotenv()

# PATH = 'http://127.0.0.1:8000'
PATH = 'https://avina.liara.run'

TOKRNEXP = datetime.now(timezone.utc) + timedelta(hours=5)

class UserView(viewsets.ViewSet):
    ExTime = 120

    @swagger_auto_schema(methods=['post'], operation_description='For Create User',
                         request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                     properties={
                                                         'FullName': openapi.Schema(type=openapi.TYPE_STRING),
                                                         'PhoneNumber': openapi.Schema(type=openapi.TYPE_STRING),
                                                         'NationalCode': openapi.Schema(type=openapi.TYPE_STRING),
                                                     }))
    @action(methods=['post'], detail=False, url_path='create')
    def create_user(self, request):
        data = request.data
        serializer = CreateUserSerializer(data=data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(data['NationalCode'], data['PhoneNumber'], data['FullName'])

        if not user:
            return Response(message_error(False, 400, error_code=216), status=status.HTTP_400_BAD_REQUEST)

        return Response(message_error(True, 200, error_code=217), status.HTTP_200_OK)



    @swagger_auto_schema(methods=['post'],
                         operation_description='For Login User',
                         request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                     properties={
                                                         'NationalCode': openapi.Schema(type=openapi.TYPE_STRING),
                                                         'Password': openapi.Schema(type=openapi.TYPE_STRING)
                                                     }
                                                     )
                         )
    @action(methods=['post'], detail=False, url_path='login')
    def login_user(self, request):
        data = request.data
        serializer = LoginUserSerializer(data=data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)

        user = User.objects.check_user_pass(data['NationalCode'], data['Password'])
        if not user:
            return Response(message_error(False, 400, error_code=218), status.HTTP_400_BAD_REQUEST)

        token = jwt.encode({'NationalCode': user.NationalCode,
                            'UserId': user.UserId,
                            'exp': TOKRNEXP }, "secret", algorithm="HS256")

        return Response(message_error(True, 200, data=token), status.HTTP_200_OK)




    @swagger_auto_schema(methods=['post'], request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                       properties={
                                                                           'PhoneNumber': openapi.Schema(type=openapi.TYPE_STRING)
                                                                       }
                                                                       ))
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



    @swagger_auto_schema(methods=['put'], request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                                                      properties={
                                                                          'Key': openapi.Schema(type=openapi.TYPE_STRING),
                                                                          'Password': openapi.Schema(type=openapi.TYPE_STRING),
                                                                          'Otp': openapi.Schema(type=openapi.TYPE_STRING),
                                                                      }
                                                                      ))
    @action(methods=['put'], detail=False, url_path='newpass')
    def set_newpass(self, request):
        data = request.data
        serializer = SetPassSerializer(data=data)
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

    @swagger_auto_schema(
        method='put',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'Password': openapi.Schema(type=openapi.TYPE_STRING)
            },
            required=['Password']
        ),
        manual_parameters=[
            openapi.Parameter(
                'Key', openapi.IN_PATH, description="Device Key", type=openapi.TYPE_STRING
            )
        ]
    )
    @action(methods=['put'], detail=False, url_path='setpass/(?P<Key>[^/.]+)')
    def set_pass(self, request, Key):
        data = request.data
        serializer = PassUserSerializer(data=data)
        if not isinstance(Key, str):
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)

        device = PassDevice.objects.filter(key=Key).first()
        if not device:
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        user = device.user
        user.Password = make_password(data['Password'])
        user.save()
        device.delete()
        return Response(message_error(True, 200, error_code=200), status.HTTP_200_OK)


class AdminPortal(viewsets.ViewSet):

    @swagger_auto_schema(methods=['put'],
                         request_body=openapi.Schema(
                             type=openapi.TYPE_OBJECT,
                             properties={
                                 'UserId': openapi.Schema(type=openapi.TYPE_STRING),
                                 'Accept': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                             }
                         ))
    @action(methods=['put'], detail=False, url_path='passiveuser/write')
    def activate_user(self, request):
        data = request.data
        serializer = ActivateUserSerializer(data=data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)

        if not data['Accept']:
            user = User.objects.filter(UserId=data['UserId']).first()
            user.delete()
            return Response(message_error(True, 204, error_code=200), status.HTTP_204_NO_CONTENT)

        user = User.objects.activate_user(data['UserId'])
        if not user:
            return Response(message_error(False, 400, error_code=221), status.HTTP_400_BAD_REQUEST)

        device = PassDevice.objects.create(user=user)
        device.save()
        path = f"{PATH}/{reverse('user-set-pass', kwargs={'Key': device.key})}"
        print(path)
        response = send_sms(path, user.PhoneNumber)
        if response != 200:
            return Response(message_error(False, 400, error_code=222), status.HTTP_400_BAD_REQUEST)
        return Response(message_error(True, 202, error_code=200), status.HTTP_202_ACCEPTED)


    @action(methods=['get'], detail=False, url_path='passiveuser/read')
    def user_passive(self, request):
        users = User.objects.filter(Active=False)
        serializer = UserDetailSerializer(users, many=True)
        return Response(message_error(True, 200, data=serializer.data), status.HTTP_200_OK)

    @swagger_auto_schema(methods=['get'],
                         manual_parameters=[
                             openapi.Parameter('UserId', openapi.IN_QUERY, required=False, type=openapi.TYPE_STRING)
                         ]
                         )
    @action(methods=['get'], detail=False, url_path='user/read')
    def user_detail(self, request):
        data = request.GET.dict()
        if not (data.get('UserId') and isinstance(data.get('UserId'), str)):
            user = User.objects.filter(Active=True,).order_by('-id')
            serializer = UserDetailSerializer(user, many=True)
            return Response(message_error(True, 200, data=serializer.data), status.HTTP_200_OK)
        user = User.objects.filter(UserId=data['UserId']).first()
        if not user:
            return Response(message_error(False, 400, error_code=201), status.HTTP_400_BAD_REQUEST)
        serializer = UserDetailSerializer(user)
        return Response(message_error(True, 200, data=serializer.data), status.HTTP_200_OK)


    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'FullName': openapi.Schema(type=openapi.TYPE_STRING),
                'NationalCode': openapi.Schema(type=openapi.TYPE_STRING),
                'PhoneNumber': openapi.Schema(type=openapi.TYPE_STRING),
            }
        )
    )
    @action(methods=['put'], detail=False, url_path='user/write')
    def user_write(self, request):
        data = request.data
        if not (data.get('UserId') and isinstance(data.get('UserId'), str)):
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(UserId=data['UserId']).first()
        if not user:
            return Response(message_error(False, 400, error_code=201),status.HTTP_400_BAD_REQUEST)
        serializer = UserWriteDetailSerializer(user, data=data, partial=True)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)

        user.FullName = serializer.validated_data.get('FullName', user.FullName)
        user.NationalCode = serializer.validated_data.get('NationalCode', user.NationalCode)
        user.PhoneNumber = serializer.validated_data.get('PhoneNumber', user.PhoneNumber)
        user.save()
        return Response(message_error(True, 200, error_code=200), status.HTTP_200_OK)


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('UserId', openapi.IN_QUERY, required=True, type=openapi.TYPE_STRING)
        ]
    )
    @action(methods=['delete'], detail=False, url_path='user/delete')
    def delete_user(self, request):
        data = request.GET.dict()
        serializer = UserDelete(data=data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        user = User.objects.filter(UserId=data['UserId'], Active=True).filter()
        if not user:
            return Response(message_error(False, 400, error_code=201), status.HTTP_400_BAD_REQUEST)
        user.delete()

        return Response(message_error(True, 204, error_code=200), status.HTTP_204_NO_CONTENT)

















