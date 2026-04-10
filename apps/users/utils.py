from django.conf import settings


def set_auth_cookies(response, access_token, refresh_token):
    is_secure = not settings.DEBUG
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,  # 자바스크립트 접근 차단 (XSS 방어)
        samesite="Lax",  # 다른 사이트에서 요청 보내는 것 일부 차단 (CSRF 방어)
        secure=is_secure,
    )

    # 2. Refresh Token (긴 수명, 토큰 재발급용)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="Lax",
        secure=is_secure,
    )

    return response


# apps/users/utils.py


def delete_auth_cookies(response):

    response.delete_cookie(
        key="access_token",
        path="/",  # 쿠키 설정 시의 path와 일치
        samesite="Lax",
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="Lax",
    )
    return response
