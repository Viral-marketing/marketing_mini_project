from django.contrib import admin
from apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("email", "name", "phone")
    list_display = ("is_staff", "is_superuser", "is_active")
    readonly_fields = ("is_staff", "is_superuser")