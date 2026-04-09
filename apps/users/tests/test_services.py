from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.users.services import create_user

User = get_user_model()


class UserService(TestCase):
    def test_create_user(self):
        # Arr
        data = {
            "email": "test@example.com",
            "name": "테스터",
            "password": "password123",
            "phone": "01012345678",
        }

        # Act
        user = create_user(**data)

        # Assert
        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))
        self.assertEqual(User.objects.count(), 1)
