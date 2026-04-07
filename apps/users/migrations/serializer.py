from rest_framework import serializers


# 요청 데이터 스펙 (Request Body)
class UserSignupRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    nickname = serializers.CharField(required=False, allow_blank=True)


# 응답 데이터 스펙 (Response Body)
class UserSignupResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    nickname = serializers.CharField(allow_blank=True, required=False)


# 예시 API 엔드포인트 스펙 설명
"""
POST /api/users/signup/
Request Body: UserSignupRequestSerializer
Response Body: UserSignupResponseSerializer
Status Code: 201 Created
"""
