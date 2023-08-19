from django.core.validators import EmailValidator, MinLengthValidator
from django.contrib.auth.password_validation import CommonPasswordValidator

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from users.models import User, Subscribe


class UserInfoSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:

        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj.id).exists()


class CreateUserSerializer(UserCreateSerializer):
    email = serializers.EmailField(validators=[EmailValidator()])
    password = serializers.CharField(validators=[MinLengthValidator(8),
                                                 CommonPasswordValidator()])

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
