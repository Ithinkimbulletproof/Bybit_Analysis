# Generated by Django 5.1.4 on 2024-12-23 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cryptopair",
            name="growth_prediction",
        ),
        migrations.AddField(
            model_name="cryptopair",
            name="is_favorite",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="cryptopair",
            name="trend",
            field=models.CharField(
                choices=[
                    ("up", "Вырастет"),
                    ("down", "Упадет"),
                    ("neutral", "Нейтрально"),
                ],
                default="neutral",
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name="cryptopair",
            name="trend_updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name="cryptopair",
            name="base_currency",
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name="cryptopair",
            name="name",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name="cryptopair",
            name="quote_currency",
            field=models.CharField(max_length=50),
        ),
    ]
