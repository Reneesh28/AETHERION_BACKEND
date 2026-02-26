from django.db import models

class RiskConfiguration(models.Model):
    total_capital = models.FloatField(default=100000)
    risk_per_trade = models.FloatField(default=0.02)
    max_exposure_per_asset = models.FloatField(default=0.20)
    max_total_exposure = models.FloatField(default=0.80)
    atr_multiplier = models.FloatField(default=1.5)
    kelly_enabled = models.BooleanField(default=False)

    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and RiskConfiguration.objects.exists():
            raise ValueError("Only one RiskConfiguration instance allowed.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("RiskConfiguration cannot be deleted.")

    def __str__(self):
        return "Aetherion Risk Configuration"

class PortfolioPosition(models.Model):
    symbol = models.CharField(max_length=50, unique=True)
    position_size = models.FloatField(default=0.0)
    average_price = models.FloatField(default=0.0)
    exposure = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.symbol} - {self.position_size}"
    
class PortfolioSummary(models.Model):
    total_capital = models.FloatField(default=0.0)
    used_capital = models.FloatField(default=0.0)
    free_capital = models.FloatField(default=0.0)
    total_exposure = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk and PortfolioSummary.objects.exists():
            raise ValueError("Only one PortfolioSummary allowed.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("PortfolioSummary cannot be deleted.")

    def __str__(self):
        return "Aetherion Portfolio Summary"

class Decision(models.Model):
    market = models.CharField(max_length=50)
    symbol = models.CharField(max_length=100)
    meta_regime = models.CharField(max_length=100)
    strategy = models.CharField(max_length=100)
    action = models.CharField(max_length=20)
    confidence = models.FloatField()
    created_at = models.DateTimeField()

    class Meta:
        db_table = "decisions"
        managed = False

class TradeExecution(models.Model):
    ACTION_CHOICES = [
        ("BUY", "BUY"),
        ("SELL", "SELL"),
    ]

    symbol = models.CharField(max_length=50)
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    position_size = models.FloatField()
    price = models.FloatField()
    capital_allocated = models.FloatField()
    meta_regime = models.CharField(max_length=50)
    strategy = models.CharField(max_length=100)
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-executed_at"]
        verbose_name = "Trade Execution"
        verbose_name_plural = "Trade Executions"

    def delete(self, *args, **kwargs):
        raise Exception("TradeExecution records are immutable and cannot be deleted.")

    def save(self, *args, **kwargs):
        if self.pk is not None:
            raise Exception("TradeExecution records are immutable and cannot be updated.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.symbol} | {self.action} | {self.position_size} @ {self.price}"

