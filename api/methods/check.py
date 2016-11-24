from api.helpers import success_response


def permission(request):
    if request.client.is_admin():
        return success_response({'status': 'admin'})

    if request.client.is_user():
        return success_response({'status': 'user'})

    return success_response({'status': 'guest'})