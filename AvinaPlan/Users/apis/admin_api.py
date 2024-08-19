from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response

from Users.models import User
from Users.serializers import CreateUserSerializer
from config import message_error

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

    @action(methods=['put'], detail=False, url_path='activete')
    def activate_user(self, request):
        pass


