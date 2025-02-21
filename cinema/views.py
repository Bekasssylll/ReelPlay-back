from django.contrib.auth import authenticate
from django.db.models import Avg
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from cinema.filter import MovieFilter
from cinema.models import Movie, SubscriptionService, TypeSubscription, Comment, FavouriteMovie, Rating
from cinema.serializers import MovieSerializer, RegisterSerializer, SubscriptionServiceSerializer, ProfileSerializer, \
    CommentSerializer, SubscriptionServiceSerializer, RatingSerializer
from django.core.mail import send_mail
from rest_framework.exceptions import NotFound

from reelsetting.settings import EMAIL_HOST_USER
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend


class MovieViewSet(viewsets.ModelViewSet):
    serializer_class = MovieSerializer
    queryset = Movie.objects.all()
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = MovieFilter

    def retrieve(self, request, *args, **kwargs):
        user = request.user
        try:
            movie = self.get_object()
        except Http404:
            raise NotFound({"message":"Неправильная ссылка"})


        if movie.type:
            user_subscription = SubscriptionService.objects.filter(user=user).order_by('-type__level').first()

            if not user_subscription:
                return Response(
                    {"message": "У вас нет подписки для доступа к этому фильму."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            if user_subscription.type.level >= movie.type.level:
                return super().retrieve(request, *args, **kwargs)

            return Response(
                {"message": "У вас недостаточный уровень подписки для просмотра этого фильма."},
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
            subject = 'Hello!'
            message = "Регистрация прошла успешно"
            from_email = EMAIL_HOST_USER
            recipient_list = [user.email, ]
            send_mail(
                subject=subject,
                message=message,
                from_email=from_email,
                recipient_list=recipient_list)

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
        serializer = SubscriptionServiceSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Подписка создана"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class AddFavouriteMovie(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        favourite_movies = FavouriteMovie.objects.filter(user=user).select_related('movie')

        if not favourite_movies.exists():
            return Response({'message': "У вас нет любимых фильмов"}, status=404)

        return Response({'List': [fav.movie.title for fav in favourite_movies]})

    def post(self, request):
        user = request.user
        movie_id = request.data.get('movie')

        if not movie_id:
            return Response({'error': "Вы не указали фильм"}, status=400)

        try:
            movie = Movie.objects.get(id=movie_id)
        except Movie.DoesNotExist:
            return Response({'error': "Фильм не найден"}, status=404)

        if FavouriteMovie.objects.filter(user=user, movie=movie).exists():
            return Response({'message': "Вы уже добавили этот фильм"}, status=400)

        FavouriteMovie.objects.create(user=user, movie=movie)
        return Response({'message': "Фильм добавлен в избранное"})

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)