# Generated by Django 5.1.4 on 2024-12-24 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_remove_cryptopair_growth_prediction_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="cryptopair",
            name="volatility_180_days",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="cryptopair",
            name="volatility_30_days",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="cryptopair",
            name="volatility_365_days",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="cryptopair",
            name="volatility_90_days",
            field=models.FloatField(blank=True, null=True),
        ),
    ]