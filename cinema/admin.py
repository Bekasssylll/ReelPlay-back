from django.contrib import admin
from django.contrib.auth import get_user_model

from cinema.models import Author, Movie,SubscriptionService, TypeSubscription, Comment, FavouriteMovie, \
    Rating


@admin.register(Movie)
class MovieRegister(admin.ModelAdmin):
    list_display = (
    'id', 'title', 'description', 'author', 'subscription', 'year', 'genre', 'category', 'type', 'type_level',
    'video_url','image')
    list_filter = ('title',)

    def type_level(self, obj):
        return obj.type.level


@admin.register(Author)
class AuthorRegister(admin.ModelAdmin):
    list_display = ('id','name',)
    list_filter = ('name',)


CustomUser = get_user_model()


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone',
                    'subscription']
    search_fields = ['username', 'email', 'phone']
    list_filter = ['subscription', 'username', 'phone']


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(SubscriptionService)
class SubscriptionServiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'type')
    list_filter = ('user', 'type')


@admin.register(TypeSubscription)
class TypeSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'level',)
    list_filter = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'text', 'created_at', 'updated_at')
    list_filter = ('movie', 'user', 'created_at', 'updated_at')


@admin.register(FavouriteMovie)
class FavouriteMovieAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie')


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'rating')
