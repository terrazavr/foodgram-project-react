from recipes.models import Tag
from rest_framework.viewsets import ReadOnlyModelViewSet
from .serializers import TagSerializer


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
