from django.conf import settings

is_secure = not settings.DEBUG

def set_auth_cookies(response, access_token, refresh_token):
    # Access Token
    response.set_cookie(
        path="/",
        key="access_token",
        value=access_token,
        httponly=True,  # 자바스크립트 접근 차단 (XSS 방어)
        samesite="Lax",  # 다른 사이트에서 요청 보내는 것 일부 차단 (CSRF 방어)
        secure=is_secure,
        # max_age는 초 단위
        max_age=int(settings.SIMPLE_JWT.get("ACCESS_TOKEN_LIFETIME").total_seconds()),
    )

    #  Refresh Token
    response.set_cookie(
        path="/",
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="Lax",
        secure=is_secure,
        max_age=int(settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME").total_seconds()),
    )

    return response


def delete_auth_cookies(response):

    response.delete_cookie(
        key="access_token",
        path="/",  # 쿠키 설정 시의 path와 일치
        samesite="Lax",
        sequre=is_secure
    )
    response.delete_cookie(
        key="refresh_token",
        path="/",
        samesite="Lax",
        secure=is_secure
    )
    return response
