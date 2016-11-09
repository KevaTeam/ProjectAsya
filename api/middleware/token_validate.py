from api.models import Token

from datetime import datetime


class User():
    log_in = False
    permission = 0

    def log_in_by_token(self, token):
        try:
            user = Token.objects.get(token=token, expires__gte=datetime.now())
            self.user_id = user.id
            self.permission = user.scope
            self.log_in = True

            return True
        except Token.DoesNotExist:
            return False

    def is_admin(self):
        return self.log_in and self.permission

    def is_user(self):
        return self.log_in

class TokenValidateMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        token = request.GET.get('access_token', None)
        request.user = User()

        if token:
            request.user.log_in_by_token(token)

        # TODO: добавить обработку события окончания игры
        print("TokenMiddleware")

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response