from rest_framework.routers import DefaultRouter

from django.urls import path

from Users.apis.api import UserView, AdminPortal, CheckToken
from Users.apis.access_api import AccessViewApi

router = DefaultRouter(trailing_slash=False)
router.register('user', UserView, basename='user')
router.register('portal', AdminPortal, basename='portal')
router.register('access', AccessViewApi, basename='access')
router.register('token', CheckToken, basename='token')


urlpatterns = []
urlpatterns += router.urls