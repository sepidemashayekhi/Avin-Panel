from rest_framework.viewsets import ViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action

from config import message_error,MyPaginationModel
from Products.models import Setting, Products, Category
from Products.serializers import CreateCategorySerializer, CategoryReadSerializer

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi



class CategoryViewSet(ViewSet):
    pagination_class = MyPaginationModel

    @swagger_auto_schema(
        request_body=openapi.Schema(type=openapi.TYPE_OBJECT,
                                    required=['Title'],
                                    properties={
                                        'Title': openapi.Schema(type=openapi.TYPE_STRING),
                                        'ParentId': openapi.Schema(type=openapi.TYPE_STRING, default=None),
                                    }
                                    )
    )
    @action(methods=['post'], detail=False, url_path='create')
    def create_category(self, request):
        data = request.data
        serializer = CreateCategorySerializer(data=data)
        if not serializer.is_valid():
            return Response(message_error(False, 400, error_code=208), status.HTTP_400_BAD_REQUEST)
        parent = Category.objects.filter(CategoryId=data.get('ParentId')).first() if data.get('ParentId') else None
        category = Category.objects.create(Title=data.get('Title'), ParentId=parent)
        return Response(message_error(True, 201, error_code=200), status.HTTP_201_CREATED)

    @swagger_auto_schema(methods=['get'],
                         manual_parameters=[
                             openapi.Parameter('CategoryId', openapi.IN_QUERY, required=False, type=openapi.TYPE_STRING),
                             openapi.Parameter('Page', openapi.IN_QUERY, required=True , type=openapi.TYPE_NUMBER)
                         ]
                         )
    @action(methods=['get'], detail=False, url_path='read')
    def read_category(self, request):
        data = request.GET.dict()
        paginator = self.pagination_class()
        if not data.get('CategoryId'):
            queryset = Category.objects.filter(ParentId=None)
            try:
                paginated_queryset = paginator.paginate_queryset(queryset, request)
                serializer = CategoryReadSerializer(paginated_queryset, many=True)
                return_data = serializer.data
            except:
                return_data = []
            return Response(message_error(True, 200, data=return_data), status.HTTP_200_OK)

        category = Category.objects.filter(CategoryId=data.get('CategoryId')).first()
        if not category:
            return Response(message_error(False, 400, error_code=226), status.HTTP_400_BAD_REQUEST)
        serializer = CategoryReadSerializer(category)
        return Response(message_error(True, 200, data=serializer.data), status.HTTP_200_OK)