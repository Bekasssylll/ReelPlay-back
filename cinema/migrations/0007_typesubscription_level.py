# Generated by Django 4.2.17 on 2025-01-04 10:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cinema", "0006_alter_comment_movie_alter_movie_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="typesubscription",
            name="level",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
