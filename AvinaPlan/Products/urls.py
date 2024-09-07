from rest_framework.routers import DefaultRouter

from Products.apis.setting_api import SettingViewSet
router = DefaultRouter()
router.register('setting', SettingViewSet, basename='setting')

urlpatterns = []
urlpatterns += router.urls
