from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserCreateSerializer, UserReadSerializer
from .services import create_user


class UserCreateAPIView(APIView):
    # 회원가입은 로그인 하지 않은 유저도 접근 허용
    permission_classes = [AllowAny]

    @extend_schema(
        summary="회원가입",
        description="이메일, 비밀번호, 이름, 전화번호를 받아 새로운 유저를 생성합니다.",
        request=UserCreateSerializer,  # 스웨거에게 "이 시리얼라이저를 참고해"라고 명시
        responses={201: UserReadSerializer},  # 응답 데이터 형식도 알려주면 금상첨화
        tags=["유저"],
    )
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
