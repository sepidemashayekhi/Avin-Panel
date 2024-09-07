from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from config import message_error
from Products.models import Setting
from Products.serializers import SettingSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SettingViewSet(ViewSet):

    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                    properties={
                                        'Value': openapi.Schema(type=openapi.TYPE_BOOLEAN)
                                    })
    )
    @action(methods=['put'], detail=False, url_path='write')
    def write_setting(self, request):
        data = request.data
        if not (data.get('Value') and isinstance(data['Value'], bool)):
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        setting = Setting.objects.filter(Title='effective_quantity').first()
        setting.Value = data['Value']
        setting.save()
        return Response(message_error(True, 200, error_code=200), status.HTTP_200_OK)

    @action(methods=['get'], detail=False, url_path='read')
    def read_setting(self, request):
        settings = Setting.objects.all()
        serializer = SettingSerializer(settings, many=True)
        return Response(message_error(True, 200, data=serializer.data), status.HTTP_200_OK)


