from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    # 목록 페이지에 표시할 필드
    list_display = ("email", "name", "phone", "is_staff", "is_active", "created_at")

    # 이메일, 닉네임, 휴대폰번호로 검색
    search_fields = ("email", "name", "phone")

    # is_staff, is_active 필터링
    list_filter = ("is_staff", "is_active")

    # 어드민 여부는 읽기 전용
    readonly_fields = ("is_superuser",)

    ordering = ("-created_at",)