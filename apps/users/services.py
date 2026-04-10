from django.contrib.auth import authenticate, get_user_model
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


def create_user(email: str, name: str, password: str, phone: str):
    user = User(email=email, name=name, phone=phone)
    user.set_password(password)
    user.save()
    return user


# 로그인 로직
def login_user(email: str, password: str):
    user = authenticate(email=email, password=password)

    if user is None:
        raise exceptions.AuthenticationFailed("없는 계정입니다")
    if not user.is_active:
        raise exceptions.AuthenticationFailed("탈퇴한 계정입니다")

    refresh = RefreshToken.for_user(user)

    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "user": user,
    }
