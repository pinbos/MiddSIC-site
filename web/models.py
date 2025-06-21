# your_app_name/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Case, When, Value, IntegerField

class Position(models.Model):
    # ... (your existing Position model code) ...
    POSITION_TYPES = (
        ('EXEC', 'Executive Committee'),
        ('PM', 'Portfolio Manager'),
        ('SA', 'Senior Analyst'),
    )

    INDUSTRY_GROUPS = (
        ('TMT', 'Tech, Media & Telecom'),
        ('RELG', 'Real Estate, Gaming & Lodging'),
        ('FI', 'Financial Institutions'),
        ('HLS', 'Healthcare & Life Sciences'),
        ('CR', 'Consumer & Retail'),
        ('NR', 'Natural Resources'),
        ('IND', 'Industrials'),
        ('NONE', 'None'),
    )

    EXEC_ROLES = (
        ('CIO', 'Chief Investment Officer'),
        ('CHAIR', 'Co-Chair'),
        ('CAO', 'Chief Administrative Officer'),
        ('COO', 'Chief Operating Officer'),
        ('NONE', 'None'),
    )

    name = models.CharField(max_length=100)
    position_type = models.CharField(max_length=4, choices=POSITION_TYPES)
    industry_group = models.CharField(max_length=5, choices=INDUSTRY_GROUPS, default='NONE')
    exec_role = models.CharField(max_length=5, choices=EXEC_ROLES, default='NONE')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    class Meta:
        ordering = [
            Case(
                When(exec_role='CHAIR', then=Value(1)),
                When(exec_role='CIO', then=Value(2)),
                When(exec_role='COO', then=Value(3)),
                When(exec_role='CAO', then=Value(4)),
                default=Value(99),
                output_field=IntegerField(),
            ),
            'name',
        ]

    def __str__(self):
        if self.position_type == 'EXEC':
            return f"{self.get_exec_role_display()}: {self.name}"
        elif self.position_type == 'PM':
            return f"PM {self.get_industry_group_display()}: {self.name}"
        else:
            return f"Senior Analyst {self.get_industry_group_display()}: {self.name}"


class Transaction(models.Model):
    # ... (your existing Transaction model code) ...
    TRANSACTION_TYPES = (
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    )

    ticker = models.CharField(max_length=10)
    transaction_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    shares = models.DecimalField(max_digits=10, decimal_places=2)
    industry_group = models.CharField(
        max_length=5,
        choices=Position.INDUSTRY_GROUPS,
        default='NONE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.transaction_type} {self.shares} shares of {self.ticker} @ ${self.price}"

class StockHolding(models.Model):
    # ... (your existing StockHolding model code) ...
    ticker = models.CharField(max_length=10, unique=True)
    shares = models.DecimalField(max_digits=10, decimal_places=2)
    cost_basis = models.DecimalField(max_digits=10, decimal_places=2)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ticker}: {self.shares} shares @ ${self.cost_basis}"

# New model for cached prices
class PriceData(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    company_name = models.CharField(max_length=255, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company_name} ({self.ticker}): ${self.price} @ {self.last_updated.strftime('%Y-%m-%d %H:%M')}"