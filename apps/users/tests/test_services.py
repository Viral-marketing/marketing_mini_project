from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import AuthenticationFailed

from apps.users.services import create_user, delete_user, login_user, update_user

User = get_user_model()


class CreateUserServiceTest(TestCase):
    def test_create_user_success(self):
        user = create_user(
            email="test@example.com",
            name="테스터",
            password="password123",
            phone="01012345678",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "테스터")
        self.assertEqual(User.objects.count(), 1)

    def test_create_user_password_is_hashed(self):
        user = create_user(
            email="test@example.com",
            name="테스터",
            password="password123",
            phone="01012345678",
        )
        self.assertNotEqual(user.password, "password123")
        self.assertTrue(user.check_password("password123"))


class UpdateUserServiceTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email="test@example.com",
            name="원래이름",
            password="password123",
            phone="01011112222",
        )

    def test_update_name_only(self):
        updated = update_user(self.user, name="변경이름", phone=None)
        self.assertEqual(updated.name, "변경이름")
        self.assertEqual(updated.phone, "01011112222")  # phone 유지

    def test_update_phone_only(self):
        updated = update_user(self.user, name=None, phone="01099998888")
        self.assertEqual(updated.name, "원래이름")  # name 유지
        self.assertEqual(updated.phone, "01099998888")

    def test_update_both_fields(self):
        updated = update_user(self.user, name="변경이름", phone="01099998888")
        self.assertEqual(updated.name, "변경이름")
        self.assertEqual(updated.phone, "01099998888")

    def test_update_persists_to_db(self):
        update_user(self.user, name="변경이름", phone=None)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, "변경이름")


class DeleteUserServiceTest(TestCase):
    def test_delete_user_success(self):
        user = create_user(
            email="test@example.com",
            name="테스터",
            password="password123",
            phone="01012345678",
        )
        self.assertEqual(User.objects.count(), 1)
        delete_user(user)
        self.assertEqual(User.objects.count(), 0)


class LoginUserServiceTest(TestCase):
    def setUp(self):
        self.user = create_user(
            email="login@example.com",
            name="로그인유저",
            password="password123",
            phone="01012345678",
        )

    def test_login_success_returns_tokens(self):
        result = login_user(email="login@example.com", password="password123")
        self.assertIn("access_token", result)
        self.assertIn("refresh_token", result)
        self.assertEqual(result["user"], self.user)

    def test_login_tokens_are_strings(self):
        result = login_user(email="login@example.com", password="password123")
        self.assertIsInstance(result["access_token"], str)
        self.assertIsInstance(result["refresh_token"], str)

    def test_login_wrong_password_fails(self):
        with self.assertRaises(AuthenticationFailed):
            login_user(email="login@example.com", password="wrongpassword")

    def test_login_nonexistent_email_fails(self):
        with self.assertRaises(AuthenticationFailed):
            login_user(email="noexist@example.com", password="password123")

    def test_login_inactive_user_fails(self):
        self.user.is_active = False
        self.user.save()
        with self.assertRaises(AuthenticationFailed):
            login_user(email="login@example.com", password="password123")
