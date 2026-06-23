from django.contrib.auth.models import AbstractUser
from django.db import models


class Account(AbstractUser):
    email = models.EmailField(unique=True)
    display_name = models.CharField(max_length=150)
    wallet_address = models.CharField(max_length=64, blank=True, null=True)
    reputation_score = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    account_credit = models.DecimalField(max_digits=20, decimal_places=9, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    REQUIRED_FIELDS = ["email", "display_name"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.username
