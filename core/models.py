from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    risk_level = models.PositiveSmallIntegerField(
        choices=[(i, f"Уровень {i}") for i in range(1, 6)],
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    favorite_pairs = models.ManyToManyField(
        "CryptoPair", blank=True, related_name="favorite_users"
    )

    def __str__(self):
        return self.user.username


class CryptoPair(models.Model):
    name = models.CharField(max_length=255, unique=True)
    base_currency = models.CharField(max_length=50)
    quote_currency = models.CharField(max_length=50)
    is_favorite = models.BooleanField(default=False)
    trend = models.CharField(
        max_length=10,
        choices=[("up", "Вырастет"), ("down", "Упадет"), ("neutral", "Нейтрально")],
        default="neutral",
    )
    trend_updated_at = models.DateTimeField(auto_now=True)
    volatility_30_days = models.FloatField(null=True, blank=True)
    volatility_90_days = models.FloatField(null=True, blank=True)
    volatility_180_days = models.FloatField(null=True, blank=True)
    volatility_365_days = models.FloatField(null=True, blank=True)

    def __str__(self):
        return self.name


class HistoricalData(models.Model):
    pair = models.ForeignKey(
        CryptoPair, on_delete=models.CASCADE, related_name="historical_data"
    )
    date = models.DateTimeField()
    open_price = models.DecimalField(max_digits=30, decimal_places=10)
    close_price = models.DecimalField(max_digits=30, decimal_places=10)
    high_price = models.DecimalField(max_digits=30, decimal_places=10)
    low_price = models.DecimalField(max_digits=30, decimal_places=10)
    volume = models.DecimalField(max_digits=30, decimal_places=10)

    class Meta:
        unique_together = ("pair", "date")
        indexes = [models.Index(fields=["date"])]

    def __str__(self):
        return f"{self.pair.name} - {self.date}"


class Strategy(models.Model):
    RISK_LEVEL_CHOICES = [("low", "Низкий"), ("medium", "Средний"), ("high", "Высокий")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="strategies")
    risk_level = models.CharField(max_length=50, choices=RISK_LEVEL_CHOICES)
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    expected_return = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Сумма должна быть больше 0.")

    def __str__(self):
        return f"Стратегия {self.user.username} ({self.risk_level}) - {self.amount}"


class RiskLevel(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
