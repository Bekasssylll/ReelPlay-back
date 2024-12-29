from django.contrib import admin
from django.contrib.auth import get_user_model

from cinema.models import Author, Movie, CustomUser, SubscriptionService, TypeSubscription


@admin.register(Movie)
class MovieRegister(admin.ModelAdmin):
    list_display = ('title', 'description', 'author', 'subscription')
    list_filter = ('title',)


@admin.register(Author)
class AuthorRegister(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)


CustomUser = get_user_model()


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'phone',
                    'subscription']  # Здесь указаны поля, которые вы хотите отображать в списке
    search_fields = ['username', 'email', 'phone']  # Возможность поиска по этим полям
    list_filter = ['subscription', 'username', 'phone']  # Фильтрация по полю 'subscription'


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(SubscriptionService)
class SubscriptionServiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'type')
    list_filter = ('user', 'type')


@admin.register(TypeSubscription)
class TypeSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
