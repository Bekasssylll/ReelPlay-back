from django.contrib.auth import authenticate
from rest_framework import viewsets, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from cinema.models import Movie, SubscriptionService, TypeSubscription
from cinema.serializers import MovieSerializer, RegisterSerializer, SubscriptionServiceSerializer, ProfileSerializer


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        movie = self.get_object()
        if movie.type:
            if not SubscriptionService.objects.filter(user=user, type=movie.type).exists():
                return Response(
                    {"message": "У вас нет доступа к этому фильму. Требуется подписка."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        return super().retrieve(request, *args, **kwargs)

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

    def post(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Профиль успешно обновлен"}, status=status.HTTP_200_OK)
        return Response({"message": "Ошибка обновления профиля!", "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)


# ViewSet для админов
class SubscriptionServiceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = SubscriptionService.objects.all()
    serializer_class = SubscriptionServiceSerializer


# APIView для активаций через endpoint
class ActivateSubscription(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        type_id = request.data.get('type')

        try:
            type_id = int(type_id)
        except (ValueError, TypeError):
            return Response(
                {"message": "Неверный формат type. Ожидается числовое значение."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            type_instance = TypeSubscription.objects.get(id=type_id)
        except TypeSubscription.DoesNotExist:
            return Response(
                {"message": "Тип подписки с таким ID не существует."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if SubscriptionService.objects.filter(user=user, type=type_instance).exists():
            return Response(
                {"message": "У этого пользователя уже существует подписка."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        SubscriptionService.objects.create(user=user, type=type_instance)
        return Response({"message": "Подписка создана"}, status=status.HTTP_201_CREATED)
