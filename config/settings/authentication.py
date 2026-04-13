from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):

    def enforce_csrf(self, request):
        # 요청을 위조하는 CSRF 공격 차단
        check = CSRFCheck(lambda req: None)
        check.process_request(request)
        reason = check.process_view(request, None, (), {})

        if reason:
            raise exceptions.PermissionDenied(f"CSRF Failed: {reason}")


    def authenticate(self, request):

        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None

        validate_token = self.get_validated_token(raw_token)
        user = self.get_user(validate_token)

        self.enforce_csrf(request)

        return user, validate_token


