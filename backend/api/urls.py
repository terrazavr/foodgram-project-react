from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import TagViewSet

app_name = 'api'

router = DefaultRouter()
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('api/', include(router.urls)),
]
