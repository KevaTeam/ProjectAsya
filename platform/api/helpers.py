from django.http import JsonResponse


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_param_or_fail(request, name, is_required=True):
    param = request.GET.get(name, False)

    if not param:
        param = request.POST.get(name, False)

    if not param and is_required:
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
    return JsonResponse({
        'error': {
            'description': 'You are not logged',
            'code': 1
        }
    })


def json_quest_schema():
    return {
        'type': 'object',
        'properties': {
            'name': { 'type': 'string' },
            'category': { 'type': 'string' },
            'description': { 'type': 'string' },
            'value': { 'type': 'number' },
            'flag_key': { 'type': 'string' },
            'author': {
                'type': ['string', 'object'],
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': { 'type': 'string' },
                        'team': { 'type': 'string' },
                        'contacts': {
                            'type': 'array',
                            'items': { 'type': 'string' }
                        }
                    }
                }
            },
            'links': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'name': { 'type': 'string' },
                        'url': { 'type': 'string' }
                    }
                }
            },
            'game': { 'type': 'string' }
        }
    }