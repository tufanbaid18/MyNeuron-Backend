from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):

    def authenticate(self, request):

        # ✅ STEP 1: Try cookie first
        raw_token = request.COOKIES.get("access_token")

        # ✅ STEP 2: If no cookie, fallback to Bearer header
        if raw_token is None:
            header = self.get_header(request)
            if header is not None:
                raw_token = self.get_raw_token(header)

        # ✅ STEP 3: If still no token → anonymous
        if raw_token is None:
            return None

        # ✅ STEP 4: Validate safely
        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            return (user, validated_token)

        except Exception:
            return None