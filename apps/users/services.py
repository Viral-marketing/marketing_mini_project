from django.contrib.auth import authenticate, get_user_model
from rest_framework import exceptions
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# 유저 CRUD
def create_user(email: str, name: str, password: str, phone: str):
    user = User(email=email, name=name, phone=phone)
    user.set_password(password)
    user.save()
    return user


def update_user(user: User, name: str, phone: str):
    if name is not None:
        user.name = name
    if phone is not None:
        user.phone = phone
    user.save()
    return user


def delete_user(user: User):
    user.delete()


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


# 리프레쉬 토큰
def refresh_access_token(refresh_token: str):

    try:
        refresh = RefreshToken(refresh_token)
        return {
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }
    except TokenError as e:
        raise exceptions.AuthenticationFailed("변조 되거난 사용한 토큰") from e
