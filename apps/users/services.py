from django.contrib.auth import get_user_model

User = get_user_model()


def create_user(email: str, name: str, password: str, phone: str):
    user = User(email=email, name=name, phone=phone)
    user.set_password(password)
    user.save()
    return user
