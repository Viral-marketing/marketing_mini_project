from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserCreateSerializer(serializers.ModelSerializer):
    # 비밀번호 확인 임시 필드
    password_confirm = serializers.CharField(
        write_only=True, min_length=8, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = ["name", "email", "password", "password_confirm", "phone"]
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 8,
                "style": {"input_type": "password"},
            }
        }

    # 이메일 중복 확인
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 존재하는 이메일")
        return value

    # 비밀번호 검증
    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        password_confirm = data.pop(
            "password_confirm", None
        )  # None인자를 줘서 필드 누락시 None 반환

        # 패스워드 확인
        if password != password_confirm:
            raise serializers.ValidationError({"password": "비밀번호 불일치"})

        # 패스워드에 이메일 아이디 포함 확인 3자리 이상 연속 중복
        email_id = email.split("@")[0].lower()
        password_low = password.lower()
        if len(email_id) >= 3:
            for i in range(len(email_id) - 2):
                chunk = email_id[i : i + 3]
                if chunk in password_low:
                    raise serializers.ValidationError(
                        {"password": "아이디 연속 3자 이상 포함"}
                    )

        return data


class UserReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["name", "email", "phone", "created_at", "updated_at"]
        read_only_fields = fields


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class UserUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=20, required=False)
    phone = serializers.CharField(max_length=15, required=False)
