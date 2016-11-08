from django.http import JsonResponse


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_param_or_fail(request, name):
    param = request.GET.get(name, False)

    if not param:
        raise Exception('Parameter ' + name + ' is not found')

    return param


def failure_response(message):
    return JsonResponse({
        'error': {
            'description': message,
        }
    })


def success_response(data):
    return JsonResponse({
        'success': 1,
        'response': data
    })


def not_logged_response():
    return failure_response({
        'error': {
            'description': 'You are not logged'
        }
    })