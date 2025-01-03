from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    phone = models.IntegerField()
    subscription = models.BooleanField(default=False)


class Author(models.Model):
    name = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.name}"


class Movie(models.Model):
    CATEGORY_CHOICES = [
        ('movie', 'Фильм'),
        ('series', 'Сериал'),
    ]

    title = models.CharField(max_length=25)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    subscription = models.BooleanField(default=False)
    category = models.CharField(
        max_length=10,
        choices=CATEGORY_CHOICES,
        default='movie'
    )

    def __str__(self):
        return f"{self.title})"


class TypeSubscription(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return "{}".format(self.name)


class SubscriptionService(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.ForeignKey(TypeSubscription, on_delete=models.CASCADE)

    def __str__(self):
        return "{} for {}".format(self.user, self.type)
