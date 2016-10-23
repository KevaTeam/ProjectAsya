from django.utils.deprecation import MiddlewareMixin
from api.models import Token

from django.http import JsonResponse
from datetime import datetime

class TokenValidateMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        token = request.GET.get('token', None)

        if token:
            user = Token.objects.filter(token=token, expires__gte=datetime.now())

            if user:
                print(user)

        print("TokenMiddleware")
        # print(response)
        return response
