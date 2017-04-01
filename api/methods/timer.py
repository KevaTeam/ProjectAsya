import time
from datetime import datetime
from django.db.models import Q

from api.models import Config
from api.helpers import get_param_or_fail, success_response, not_logged_response


def get_action(request):
    if not request.client.log_in:
        return not_logged_response()

    timestamps = Config.objects.filter(
        Q(key='start') | Q(key='end')
    )
    now = time.time()

    data = {}
    for timestamp in timestamps:
        dt = datetime.strptime(timestamp.value, '%d-%m-%Y %H:%M:%S')
        diff = int(int(dt.timestamp()) - now)

        data[timestamp.key] = {
            'date': dt,
            'delta': diff if diff > 0 else 0
        }

    return success_response(data)


def set_action(request):
    if not request.client.is_admin():
        return not_logged_response()

    time_start = get_param_or_fail(request, 'start')
    time_end = get_param_or_fail(request, 'end')

    print(time_start, time_end)
    try:
        start = Config.objects.get(key='start')
        end = Config.objects.get(key='end')

        start.value = time_start
        end.value = time_end
    except Config.DoesNotExist:
        start = Config(key='start', value=time_start)
        end = Config(key='end', value=time_end)

    start.save()
    end.save()

    return success_response({})


def current_action(request):
    return success_response({
        'timestamp': int(time.time()),
        'datetime': datetime.now()
    })