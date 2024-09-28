from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from config import message_error
from Products.models import Setting, Products
from Products.serializers import ProductCreateSerializer, ProductReadSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class ProductViewSet(ViewSet):

    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                    properties={
                                        'Title': openapi.Schema(type=openapi.TYPE_STRING),
                                        'CategoryId': openapi.Schema(type=openapi.TYPE_STRING),
                                        'Price': openapi.Schema(type=openapi.TYPE_NUMBER),
                                        'Quantity': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    }
                                    )
    )
    @action(methods=['post'], detail=False, url_path='create')
    def create_product(self, request):
        data = request.data
        serializer = ProductCreateSerializer(data=data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        serializer.save()
        return Response(message_error(True, 201, error_code=20), status.HTTP_201_CREATED)

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('ProductId', openapi.IN_QUERY, required=False, type=openapi.TYPE_STRING)
    ])
    @action(methods=['get'], detail=False, url_path='read')
    def read_product(self, request):
        data = request.GET.dict()
        if data.get('ProductId'):
            product = Products.objects.filter(ProductId=data.get('ProductId')).first()
            serializer = ProductReadSerializer(product)
            return Response(message_error(True, 200, data=serializer.data), status.HTTP_200_OK)
        products = Products.objects.all().order_by('-id')
        serializer = ProductReadSerializer(products, many=True)
        return Response(message_error(True, 200, data=serializer.data), status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('ProductId',openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True)
        ]
    )
    @action(methods=['delete'], detail=False, url_path='delete')
    def delete_product(self, request):
        data = request.GET.dict()
        if not data.get('ProductId') or not isinstance(data['ProductId'], str):
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        product = Products.objects.filter(ProductId=data.get('ProductId')).first()
        if not Products:
            return Response(message_error(False, 400, error_code=225), status.HTTP_400_BAD_REQUEST)
        product.delete()
        return Response(message_error(True, 204, error_code=200), status.HTTP_204_NO_CONTENT)





