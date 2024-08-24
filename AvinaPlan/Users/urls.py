from rest_framework.routers import DefaultRouter

from django.urls import path

from Users.apis.api import UserView, AdminPortal

router = DefaultRouter()
router.register('user', UserView, basename='user')
router.register('portal', AdminPortal, basename='portal')

urlpatterns = []
urlpatterns += router.urls