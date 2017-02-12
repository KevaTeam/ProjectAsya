from django.contrib.auth.hashers import check_password, make_password
from django.db.utils import IntegrityError
from api.models import User, Token
from api.helpers import (
    get_param_or_fail, failure_response, get_client_ip,
    success_response
)
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

import time

def auth(request):
    try:
        username = get_param_or_fail(request, 'username')
        password = get_param_or_fail(request, 'password')

        user = User.objects.get(name=username)

    except User.DoesNotExist:
        return failure_response('The user with same username or password does not exists')
    except Exception as e:
        return failure_response(e.args[0])

    if not check_password(password, user.password):
        return failure_response('The user with same username or password does not exists')

    ip = get_client_ip(request)
    print(user)

    token = Token()

    token.generate(user, ip)
    token.save()

    return success_response({
        'access_token': token.token,
        'user_id': user.id,
        'expires_in': int(token.expires.timestamp()),
        'role': user.role
    })


def signup(request):
    try:
        username = get_param_or_fail(request, 'username')
        password = get_param_or_fail(request, 'password')
        mail = request.GET.get('mail', 'undefined' + str(time.time()) + '@example.com')

        validate_email(mail)

        password = make_password(password)

        user = User.objects.filter(name=username)
        if user:
            return failure_response('The user with same username is already exists')

        user = User.objects.filter(mail=mail)
        if user:
            return failure_response('The user with same email is already exists')

        # Проверяем существуют ли другие пользователи,
        # Если нет, то даем ему админские права
        count_user = User.objects.all().count()
        user_role = 2 if count_user == 0 else 1

        user = User(
            name=username,
            mail=mail,
            password=password,
            role=user_role
        )

        user.save()

    except ValidationError:
        return failure_response('The email is not valid')
    except User.DoesNotExist:
        return failure_response('The user with same username does not exists')
    except IntegrityError as e:
        return failure_response(e.args[0])
    except Exception as e:
        return failure_response(e.args[0])

    return success_response({'id': user.id})