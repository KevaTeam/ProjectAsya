from django.http import HttpResponse
from api.models import Token
from datetime import datetime

class Client():
    log_in = False
    permission = 0

    def log_in_by_token(self, token):
        try:
            user = Token.objects.get(token=token, expires__gte=datetime.now())

            self.user = user.uid
            self.user_id = user.uid.id
            self.permission = user.scope
            self.log_in = True

            return True
        except Token.DoesNotExist:
            return False

    def is_admin(self):
        print(self.permission)
        return self.log_in and self.permission == 2

    def is_user(self):
        return self.log_in

class TokenValidateMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def process_request(self, request):
        return HttpResponse("in exception")

    def __call__(self, request):
        token = request.GET.get('access_token', None) or request.POST.get('access_token', None)
        request.client = Client()

        if token:
            request.client.log_in_by_token(token)

        # TODO: добавить обработку события окончания игры

        # Code to be executed for each request before
        # the view (and later middleware) are called.

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def process_exception(self, request, exception):
        return HttpResponse("exception occured :(")