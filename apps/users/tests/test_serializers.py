from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from apps.users.serializers import UserCreateSerializer, UserUpdateSerializer

User = get_user_model()


class UserCreateSerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            "email": "newuser@example.com",
            "name": "신규유저",
            "password": "secure_password123",
            "password_confirm": "secure_password123",
            "phone": "01099998888",
        }

    def test_valid_data_passes(self):
        serializer = UserCreateSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())

    def test_password_mismatch_fails(self):
        data = {**self.valid_data, "password_confirm": "different_password123"}
        serializer = UserCreateSerializer(data=data)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("비밀번호 불일치", str(cm.exception))

    def test_duplicate_email_fails(self):
        User.objects.create_user(
            email=self.valid_data["email"],
            password="somepassword123",
            name="기존유저",
            phone="01011112222",
        )
        serializer = UserCreateSerializer(data=self.valid_data)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("user with this email already exists", str(cm.exception))

    def test_password_too_short_fails(self):
        data = {**self.valid_data, "password": "short", "password_confirm": "short"}
        serializer = UserCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_password_contains_email_id_fails(self):
        data = {
            **self.valid_data,
            "email": "admin@example.com",
            "password": "admin123456",
            "password_confirm": "admin123456",
        }
        serializer = UserCreateSerializer(data=data)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("아이디 연속 3자 이상 포함", str(cm.exception))

    def test_password_email_id_case_insensitive_check(self):
        """이메일 아이디 대문자가 포함돼도 검증이 동작해야 함"""
        data = {
            **self.valid_data,
            "email": "UserABC@example.com",
            "password": "myuserabc123",
            "password_confirm": "myuserabc123",
        }
        serializer = UserCreateSerializer(data=data)
        with self.assertRaises(ValidationError) as cm:
            serializer.is_valid(raise_exception=True)
        self.assertIn("아이디 연속 3자 이상 포함", str(cm.exception))

    def test_short_email_id_skips_check(self):
        """이메일 아이디가 2자 이하면 비밀번호 포함 검사를 건너뜀"""
        data = {
            **self.valid_data,
            "email": "ab@example.com",
            "password": "myab12345678",
            "password_confirm": "myab12345678",
        }
        serializer = UserCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_password_confirm_not_in_validated_data(self):
        """password_confirm은 validated_data에서 제거돼야 함"""
        serializer = UserCreateSerializer(data=self.valid_data)
        serializer.is_valid(raise_exception=True)
        self.assertNotIn("password_confirm", serializer.validated_data)


class UserUpdateSerializerTest(TestCase):
    def test_name_only_valid(self):
        serializer = UserUpdateSerializer(data={"name": "변경이름"})
        self.assertTrue(serializer.is_valid())

    def test_phone_only_valid(self):
        serializer = UserUpdateSerializer(data={"phone": "01099991111"})
        self.assertTrue(serializer.is_valid())

    def test_both_fields_valid(self):
        serializer = UserUpdateSerializer(
            data={"name": "변경이름", "phone": "01099991111"}
        )
        self.assertTrue(serializer.is_valid())

    def test_empty_data_valid(self):
        """두 필드 모두 required=False이므로 빈 요청도 유효"""
        serializer = UserUpdateSerializer(data={})
        self.assertTrue(serializer.is_valid())
