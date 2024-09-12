from rest_framework.routers import DefaultRouter

from Products.apis.setting_api import SettingViewSet
from Products.apis.product_api import ProductViewSet
router = DefaultRouter()
router.register('setting', SettingViewSet, basename='setting')
router.register('product', ProductViewSet, basename='product')

urlpatterns = []
urlpatterns += router.urls
