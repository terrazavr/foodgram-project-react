from rest_framework import serializers
from rest_framework.validators import UniqueValidator
# from rest_framework.validators import UniqueValidator

from users.models import Subscribe, User


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:

        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        is_subscribed = Subscribe.objects.filter(
            author=obj, subscriber=user
            ).exists()
        return is_subscribed


class UserCreateSerializer(serializers.ModelSerializer):
    """Сериалайзер для модели User."""
    username = serializers.CharField(
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(
        max_length=254,
        validators=[UniqueValidator(queryset=User.objects.all())])
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    class Meta:

        model = User
        fields = ('email', 'id', 'username',
                  'password', 'first_name', 'last_name')
