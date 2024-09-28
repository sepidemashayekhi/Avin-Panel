from rest_framework import serializers

from Products.models import Setting, Category, Products

class SettingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Setting
        fields = '__all__'


class ProductCreateSerializer(serializers.ModelSerializer):
    CategoryId = serializers.CharField()

    class Meta:
        model = Products
        fields = ['Title', 'CategoryId', 'Price', 'Quantity']

    def to_internal_value(self, data):
        internal_data = super().to_internal_value(data)

        try:
            category = Category.objects.get(UserId=internal_data['CategoryId'])
        except Category.DoesNotExist:
            raise serializers.ValidationError({"CategoryId": "Category not found"})

        internal_data['CategoryId'] = category
        return internal_data
    def create(self, validated_data):
        # for item in validated_data:
        product = Products.objects.create(
            Title=validated_data['Title'],
            CategoryId=validated_data['CategoryId'],
            Price=validated_data['Price'],
            Quantity=validated_data['Quantity'],
        )
        return product

class ProductReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Products
        fields = ['ProductId','Title', 'CategoryId', 'Price', 'Quantity']

class CreateCategorySerializer(serializers.Serializer):
    Title = serializers.CharField(max_length=50, allow_null=False, allow_blank=False, required=True)
    ParentId = serializers.CharField(max_length=50, required=False, allow_null=True)

class CategoryReadSerializer(serializers.ModelSerializer):
    Children = serializers.SerializerMethodField()
    class Meta:
        model = Category
        fields = ['CategoryId', 'Title', 'Children']

    def get_Children(self, obj):
        parent_id = Category.objects.filter(CategoryId=obj.CategoryId).first()
        children = Category.objects.filter(ParentId=parent_id.id)
        return CategoryReadSerializer(children, many=True).data

