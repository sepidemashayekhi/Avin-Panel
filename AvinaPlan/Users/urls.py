from rest_framework.routers import DefaultRouter

from django.urls import path

from Users.apis.api import UserView, AdminPortal
from Users.apis.access_api import AccessViewApi

router = DefaultRouter()
router.register('user', UserView, basename='user')
router.register('portal', AdminPortal, basename='portal')
router.register('access', AccessViewApi, basename='access')


urlpatterns = []
urlpatterns += router.urls