import time
from datetime import datetime
from django.db.models import Q

from api.models import Setting
from api.helpers import success_response, not_logged_response


def get(request):
    if not request.client.log_in:
        return not_logged_response()

    timestamps = Setting.objects.filter(
        Q(key='start') | Q(key='end')
    )
    print(timestamps)
    now = time.time()

    data = {}
    for timestamp in timestamps:
        diff = int(int(timestamp.value) - now)

        data[timestamp.key] = diff if diff > 0 else 0


    return success_response(data)


def current(request):
    return success_response({
        'timestamp': int(time.time()),
        'datetime': datetime.now()
    })