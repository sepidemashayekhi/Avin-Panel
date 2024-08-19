from rest_framework.routers import DefaultRouter

from django.urls import path

from Users.apis.admin_api import UserPortal

router = DefaultRouter()
router.register('user', UserPortal, basename='user')

urlpatterns = []
urlpatterns += router.urls