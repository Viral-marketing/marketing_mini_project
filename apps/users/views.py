from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserCreateSerializer, UserLoginSerializer, UserReadSerializer
from .services import create_user, login_user
from .utils import delete_auth_cookies, set_auth_cookies


class UserCreateAPIView(APIView):
    # 회원가입은 로그인 하지 않은 유저도 접근 허용
    permission_classes = [AllowAny]

    @extend_schema(
        summary="회원가입",
        description="이메일, 비밀번호, 이름, 전화번호를 받아 새로운 유저를 생성",
        request=UserCreateSerializer,  # 요청 데이터 형식
        responses={201: UserReadSerializer},  # 응답 데이터 형식
        tags=["사용자 관리"],
    )
    def post(self, request):
        # 시리얼 라이저로 검증
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = create_user(
            email=serializer.validated_data["email"],
            name=serializer.validated_data["name"],
            password=serializer.validated_data["password"],
            phone=serializer.validated_data["phone"],
        )
        response_serializer = UserReadSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# 로그인 기능 구현


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="로그인",
        description="이메일과 비밀번호로 로그인하고, JWT 토큰을 HttpOnly 쿠키에 저장",
        request=UserLoginSerializer,  # 요청 데이터 형식
        responses={
            200: OpenApiResponse(description="로그인 성공 (Set-Cookie)"),
            401: OpenApiResponse(description="인증 실패 (비밀번호 오류 또는 탈퇴)"),
        },
        tags=["인증"],
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        result = login_user(email=email, password=password)

        response_data = {
            "status": "success",
            "user": UserReadSerializer(result["user"]).data,
        }
        response = Response(response_data, status=status.HTTP_200_OK)

        return set_auth_cookies(
            response=response,
            access_token=result["access_token"],
            refresh_token=result["refresh_token"],
        )


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="로그아웃",
        description="리프레쉬 토큰 블랙리스트 등록 쿠키 삭제",
        responses={200: OpenApiResponse(description="로그아웃 성공")},
        tags=["인증"],
    )
    def post(self, request):
        response = Response(status=status.HTTP_200_OK)

        try:
            refresh_tocken = request.COOKIES.get("refresh_token")

            if refresh_tocken:
                token = RefreshToken(refresh_tocken)
                token.blacklist()

        except Exception:
            pass

        return delete_auth_cookies(response)
