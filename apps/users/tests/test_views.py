from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class UserAPITest(APITestCase):
    def test_signup_api_success(self):
        # Arrange
        url = reverse("users:register")  # urls.py에 설정된 name
        data = {
            "email": "newuser@example.com",
            "name": "신규유저",
            "password": "secure_password123",
            "password_confirm": "secure_password123",
            "phone": "01099998888",
        }

        # Act
        response = self.client.post(url, data, format="json")

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], data["email"])
        self.assertNotIn("password", response.data)  # 응답에 비밀번호 미포함 확인
