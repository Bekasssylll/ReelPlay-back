from django.contrib.auth import authenticate
from rest_framework import viewsets, request, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken

from cinema.models import Movie, CustomUser, SubscriptionService, TypeSubscription
from cinema.serializers import MovieSerializer, RegisterSerializer, SubscriptionServiceSerializer, ProfileSerializer
from rest_framework.authtoken.models import Token


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create', 'update', 'partial_update',
                             'destroy']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAdminUser]
        return [permission() for permission in permission_classes]


class RegisterApiView(APIView):

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user, access_token = serializer.save()
            return Response({"message": "Успешная регистрация", "Token": access_token, },
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            raise AuthenticationFailed("Неверное имя пользователя или пароль.")

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        return Response({
            "message": "Вы успешно вошли!",
            "token": access_token,
        }, status=status.HTTP_200_OK)


class ProfileApiView(APIView):
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SubscriptionServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SubscriptionService.objects.all()
    serializer_class = SubscriptionServiceSerializer


class ActivateSubscription(APIView):
    def post(self, request):
        serializer = SubscriptionServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Подписка оформлена"})
        return Response(serializer.errors)
