# Generated by Django 4.2.17 on 2025-01-28 17:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("cinema", "0007_typesubscription_level"),
    ]

    operations = [
        migrations.AddField(
            model_name="movie",
            name="video_url",
            field=models.URLField(blank=True, null=True),
        ),
    ]
