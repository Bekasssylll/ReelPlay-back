from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from cinema.models import Movie, CustomUser, SubscriptionService, Comment, TypeSubscription


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')  # Возвращает только имя пользователя

    class Meta:
        model = Comment
        fields = ['user', 'movie', 'text']


class MovieSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ['title', 'description', 'author', 'comments']


class RegisterSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    subscription = serializers.BooleanField(required=False)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email', 'phone', 'subscription', 'password1', 'password2']

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Пароли не совпадают.")
        data.pop('password2')
        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
            password=validated_data['password1'],
        )
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        return user, access_token


class SubscriptionServiceSerializer(serializers.Serializer):
    type = serializers.IntegerField()

    def validate_type(self, value):
        try:
            type_instance = TypeSubscription.objects.get(id=value)
        except TypeSubscription.DoesNotExist:
            raise serializers.ValidationError("Тип подписки с таким ID не существует.")
        return type_instance

    def create(self, validated_data):
        user = self.context['request'].user
        type_instance = validated_data['type']

        if SubscriptionService.objects.filter(user=user, type=type_instance).exists():
            raise serializers.ValidationError("У этого пользователя уже существует подписка.")

        return SubscriptionService.objects.create(user=user, type=type_instance)


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'phone', 'email']
