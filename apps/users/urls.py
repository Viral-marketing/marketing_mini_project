from django.urls import path

from apps.users import views

app_name = "users"

urlpatterns = [
    path("register/", views.UserCreateAPIView.as_view(), name="register"),
]
