from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserCreateSerializer, UserReadSerializer
from .services import create_user


class UserCreateAPIView(APIView):
    # 회원가입은 로그인 하지 않은 유저도 접근 허용
    permission_classes = [AllowAny]

    def post(self, request):
        # 시리얼 라이저로 검증
        serializer = UserCreateSerializer(data=request.data)
        # raise_exception=True 검증 실패시 400_error 반환
        serializer.is_valid(raise_exception=True)

        user = create_user(
            email=serializer.validated_data["email"],
            name=serializer.validated_data["name"],
            password=serializer.validated_data["password"],
            phone=serializer.validated_data["phone"],
        )
        response_serializer = UserReadSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
