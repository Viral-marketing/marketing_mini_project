from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.users.serializers import UserCreateSerializer


class UserSerializerTest(TestCase):
    def test_password_contains_email_id_fails(self):
        # Arr
        data = {
            "email": "admin@example.com",
            "name": "관리자",
            "password": "admin123",
            "password_confirm": "admin123",
            "phone": "01011112222",
        }
        serializer = UserCreateSerializer(data=data)

        # Act & Assert
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)

        self.assertIn("아이디 연속 3자 이상 포함", str(cm.exception))
