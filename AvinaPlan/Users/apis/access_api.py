from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from config import message_error, send_sms
from Users.serializers import UserAccessSerializer
from Users.models import Access, UserAccess, Menu, User


class AccessViewApi(viewsets.ViewSet):

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'UserId': openapi.Schema(type=openapi.TYPE_STRING),
                    'MenuId': openapi.Schema(type=openapi.TYPE_STRING),
                    'AccessId': openapi.Schema(type=openapi.TYPE_STRING),
                }
            )

        )
    )
    @action(methods=['post'], detail=False, url_path='create')
    def create_access(self, request):
        data = request.data
        serializer = UserAccessSerializer(data=data, many=True)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(message_error(True, 201, error_code=200), status.HTTP_201_CREATED)

