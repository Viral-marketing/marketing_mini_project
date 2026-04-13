from django.urls import path

from apps.users import views

app_name = "users"

urlpatterns = [
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
    path("login/", views.LoginAPIView.as_view(), name="login"),
    path("logout/", views.LogoutAPIView.as_view(), name="logout"),
    path("profile/", views.UserProfieAPIView.as_view(), name="profile"),
]
