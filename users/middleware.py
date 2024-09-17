# middleware.py
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
import json
from django.http import JsonResponse


class JWTResponseMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.method == 'POST':
            try:
                request._body = request.body  # Cache the body
            except Exception:
                request._body = b''  # Fallback to empty byte string

    def process_response(self, request, response):
        if response.status_code == 204 and request.path == '/auth/registration/':
            if request.method == 'POST':
                try:
                    body = json.loads(request._body)
                    user_email = body.get('username')
                    if user_email:
                        User = get_user_model()
                        try:
                            user = User.objects.get(email=user_email)
                            refresh = RefreshToken.for_user(user)
                            response_data = {
                                'access': str(refresh.access_token),
                                'refresh': str(refresh),
                            }
                            response = JsonResponse(response_data)
                        except User.DoesNotExist:
                            pass
                except json.JSONDecodeError:
                    pass
        return response
