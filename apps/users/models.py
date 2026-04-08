from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    name = models.CharField(max_length=20, null=False, blank=False)
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    password = models.CharField(max_length=128)
    phone = models.CharField(max_length=15, null=False, blank=False)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone"]

    class Meta:
        db_table = "user"
        verbose_name_plural = "users"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.name}{self.email}"
