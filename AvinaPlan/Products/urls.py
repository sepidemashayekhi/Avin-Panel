from rest_framework.routers import DefaultRouter

from Products.apis.setting_api import SettingViewSet
from Products.apis.product_api import ProductViewSet
from Products.apis.category_api import CategoryViewSet
router = DefaultRouter(trailing_slash=False)
router.register('setting', SettingViewSet, basename='setting')
router.register('product', ProductViewSet, basename='product')
router.register('category', CategoryViewSet, basename='category')

urlpatterns = []
urlpatterns += router.urls
