from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.services import create_user


class UserCreateAPIViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("users:register")
        self.valid_data = {
            "email": "newuser@example.com",
            "name": "신규유저",
            "password": "secure_password123",
            "password_confirm": "secure_password123",
            "phone": "01099998888",
        }

    def test_signup_success(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], self.valid_data["email"])
        self.assertEqual(response.data["name"], self.valid_data["name"])

    def test_signup_response_excludes_password(self):
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertNotIn("password", response.data)

    def test_signup_duplicate_email_fails(self):
        create_user(
            email=self.valid_data["email"],
            name="기존유저",
            password="password123",
            phone="01011112222",
        )
        response = self.client.post(self.url, self.valid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_password_mismatch_fails(self):
        data = {**self.valid_data, "password_confirm": "different_password123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_password_contains_email_id_fails(self):
        data = {
            **self.valid_data,
            "email": "admin@example.com",
            "password": "admin123456",
            "password_confirm": "admin123456",
        }
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_short_password_fails(self):
        data = {**self.valid_data, "password": "short", "password_confirm": "short"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_missing_required_field_fails(self):
        data = {**self.valid_data}
        del data["email"]
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPIViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("users:login")
        self.user = create_user(
            email="login@example.com",
            name="로그인유저",
            password="password123",
            phone="01012345678",
        )

    def test_login_success_status(self):
        data = {"email": "login@example.com", "password": "password123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_success_sets_cookies(self):
        data = {"email": "login@example.com", "password": "password123"}
        response = self.client.post(self.url, data, format="json")
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_login_cookies_are_httponly(self):
        data = {"email": "login@example.com", "password": "password123"}
        response = self.client.post(self.url, data, format="json")
        self.assertTrue(response.cookies["access_token"]["httponly"])
        self.assertTrue(response.cookies["refresh_token"]["httponly"])

    def test_login_response_body(self):
        data = {"email": "login@example.com", "password": "password123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.data["status"], "success")
        self.assertEqual(response.data["user"]["email"], "login@example.com")
        self.assertNotIn("password", response.data["user"])

    def test_login_wrong_password_fails(self):
        data = {"email": "login@example.com", "password": "wrongpassword"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_nonexistent_email_fails(self):
        data = {"email": "noexist@example.com", "password": "password123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_inactive_user_fails(self):
        self.user.is_active = False
        self.user.save()
        data = {"email": "login@example.com", "password": "password123"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutAPIViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("users:logout")
        self.user = create_user(
            email="logout@example.com",
            name="로그아웃유저",
            password="password123",
            phone="01012345678",
        )

    def test_logout_unauthenticated_fails(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_success(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_logout_clears_cookies(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(self.url)
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")

    def test_logout_blacklists_refresh_token(self):
        """블랙리스트 등록된 토큰으로 재로그인 시도 불가 확인"""
        self.client.force_authenticate(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["refresh_token"] = str(refresh)
        self.client.post(self.url)

        from rest_framework_simplejwt.exceptions import TokenError

        with self.assertRaises(TokenError):
            RefreshToken(str(refresh)).blacklist()


class UserProfileAPIViewTest(APITestCase):
    def setUp(self):
        self.url = reverse("users:profile")
        self.user = create_user(
            email="profile@example.com",
            name="프로필유저",
            password="password123",
            phone="01012345678",
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile_success(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "profile@example.com")
        self.assertEqual(response.data["name"], "프로필유저")

    def test_get_profile_excludes_password(self):
        response = self.client.get(self.url)
        self.assertNotIn("password", response.data)

    def test_get_profile_unauthenticated_fails(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_name_success(self):
        response = self.client.patch(self.url, {"name": "변경이름"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "변경이름")

    def test_patch_phone_success(self):
        response = self.client.patch(self.url, {"phone": "01099998888"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["phone"], "01099998888")

    def test_patch_both_fields_success(self):
        data = {"name": "변경이름", "phone": "01099998888"}
        response = self.client.patch(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "변경이름")
        self.assertEqual(response.data["phone"], "01099998888")

    def test_delete_user_success(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_removes_from_db(self):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        self.client.delete(self.url)
        self.assertFalse(User.objects.filter(email="profile@example.com").exists())

    def test_delete_clears_cookies(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.cookies["access_token"].value, "")
        self.assertEqual(response.cookies["refresh_token"].value, "")
