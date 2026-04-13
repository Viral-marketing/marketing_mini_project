import logging
from tokenize import TokenError

from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    UserCreateSerializer,
    UserLoginSerializer,
    UserReadSerializer,
    UserUpdateSerializer,
)
from .services import (
    create_user,
    delete_user,
    login_user,
    refresh_access_token,
    update_user,
)
from .utils import delete_auth_cookies, set_auth_cookies

logger = logging.getLogger(__name__)


class UserCreateAPIView(APIView):
    # 회원가입은 로그인 하지 않은 유저도 접근 허용
    permission_classes = [AllowAny]

    @extend_schema(
        summary="회원가입",
        description="이메일, 비밀번호, 이름, 전화번호를 받아 새로운 유저를 생성",
        request=UserCreateSerializer,  # 요청 데이터 형식
        responses={201: UserReadSerializer},  # 응답 데이터 형식
        tags=["user CRUD"],
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
            refresh_token = request.COOKIES.get("refresh_token")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

        except Exception as e:
            logger.warning(f" 토큰 블랙리스트 등록 실패: {e}")

        return delete_auth_cookies(response)


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="유저 프로필 조회",
        tags=["user CRUD"],
        responses={200: UserReadSerializer},
    )
    def get(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="유저 프로필 수정",
        tags=["user CRUD"],
        request=UserUpdateSerializer,
        responses={200: UserReadSerializer},
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_user = update_user(
            request.user,
            serializer.validated_data.get("name"),
            serializer.validated_data.get("phone"),
        )
        response_serializer = UserReadSerializer(updated_user)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        summary="회원탈퇴",
        tags=["user CRUD"],
        responses={204: OpenApiResponse(description="탈퇴 성공")},
    )
    def delete(self, request):
        delete_user(request.user)

        response = Response( status=status.HTTP_204_NO_CONTENT)
        # 탈퇴후 쿠키 삭제
        return delete_auth_cookies(response)


class TokenRefreshAPIView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Token 갱신",
        description="쿠키에 저장된 리프레쉬 토큰으로 새 토큰을 발급",
        responses={
            200: OpenApiResponse(description="토큰 갱신 성(Set-Cookie)"),
            401: OpenApiResponse(description="리프레쉬 토크 없음 또는 만료"),
        },
        tags=["인증"],
    )
    def post(self, request):

        refresh_token_value = request.COOKIES.get("refresh_token")

        if not refresh_token_value:
            return Response(
                {"detail": "refresh token이 존재 하지 않음"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            tokens = refresh_access_token(refresh_token_value)
        except TokenError:
            return Response(
                {"detail": "유효하지 않은 토큰"}, status=status.HTTP_401_UNAUTHORIZED
            )

        response = Response({"status": "토큰 발금 성공"}, status=status.HTTP_200_OK)
        return set_auth_cookies(
            response=response,
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )
