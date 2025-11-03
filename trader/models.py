from django.db import models
from django.utils import timezone


class Account(models.Model):
    """Simple single-account model holding cash balance."""
    name = models.CharField(max_length=100, default="Default Account")
    cash = models.DecimalField(max_digits=20, decimal_places=2, default=100000.00)

    def __str__(self):
        return f"{self.name} (${self.cash})"


class Position(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="positions")
    symbol = models.CharField(max_length=20)
    quantity = models.IntegerField(default=0)
    avg_price = models.DecimalField(max_digits=20, decimal_places=4, default=0)

    class Meta:
        unique_together = ("account", "symbol")

    def __str__(self):
        return f"{self.symbol}: {self.quantity} @ {self.avg_price}"


class Trade(models.Model):
    SIDE_CHOICES = (("BUY", "Buy"), ("SELL", "Sell"))
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name="trades")
    symbol = models.CharField(max_length=20)
    side = models.CharField(max_length=4, choices=SIDE_CHOICES)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=20, decimal_places=4)
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.timestamp.isoformat()} {self.side} {self.quantity} {self.symbol} @ {self.price}"
from django.db import models

# Create your models here.
