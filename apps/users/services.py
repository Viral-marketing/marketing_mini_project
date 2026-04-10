from django.contrib.auth import authenticate, get_user_model
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# 유저 CRUD
def create_user(email: str, name: str, password: str, phone: str):
    user = User(email=email, name=name, phone=phone)
    user.set_password(password)
    user.save()
    return user
def read_user(user: User):
    return {
        "email": user.email,
    }


def update_user(user: User, email: str, name: str, phone: str):



def delete_user(user: User):





# 로그인 로직
def login_user(email: str, password: str):
    user = authenticate(email=email, password=password)

    if user is None:
        raise exceptions.AuthenticationFailed("없는 계정입니다")
    if user.is_active == False:
        raise exceptions.AuthenticationFailed("탈퇴한 계정입니다")

    refresh = RefreshToken.for_user(user)

    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
        "user": user,
    }
