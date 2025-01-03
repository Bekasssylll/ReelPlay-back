"""
URL configuration for reelsetting project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from cinema.views import MovieViewSet, RegisterApiView, LoginApiView, SubscriptionServiceViewSet, ProfileApiView, \
    ActivateSubscription, CommentViewSet

router = SimpleRouter()
router.register(r"movie", MovieViewSet, basename='movie')
router.register(r"subscription", SubscriptionServiceViewSet, basename='subscription')
router.register(r"comment", CommentViewSet, basename='Comment')

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', include(router.urls)),
    path('register/', RegisterApiView.as_view()),
    path('login/', LoginApiView.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('profile/', ProfileApiView.as_view(), name='profile'),
    path('activate/', ActivateSubscription.as_view(), name='activate')
]
