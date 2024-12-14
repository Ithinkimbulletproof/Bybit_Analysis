from django.db import models


class User(models.Model):
    username = models.CharField(max_length=100, unique=True)
    risk_level = models.IntegerField(choices=[(i, f"Уровень {i}") for i in range(1, 6)])
    favorite_pairs = models.ManyToManyField(
        "CryptoPair", blank=True, related_name="favorite_users"
    )

    def __str__(self):
        return self.username


class CryptoPair(models.Model):
    name = models.CharField(max_length=50, unique=True)
    base_currency = models.CharField(max_length=20)
    quote_currency = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class HistoricalData(models.Model):
    pair = models.ForeignKey(CryptoPair, on_delete=models.CASCADE)
    date = models.DateTimeField()
    open_price = models.DecimalField(max_digits=30, decimal_places=10)
    close_price = models.DecimalField(max_digits=30, decimal_places=10)
    high_price = models.DecimalField(max_digits=30, decimal_places=10)
    low_price = models.DecimalField(max_digits=30, decimal_places=10)
    volume = models.DecimalField(max_digits=30, decimal_places=10)

    class Meta:
        unique_together = ("pair", "date")

    def __str__(self):
        return f"{self.pair.name} - {self.date}"


class Strategy(models.Model):
    risk_level = models.IntegerField(choices=[(i, f"Уровень {i}") for i in range(1, 6)])
    parameters = models.TextField()
    expected_return = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Стратегия {self.risk_level}"
