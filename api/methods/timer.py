from django.db.models import Q
from api.models import Setting
from api.helpers import success_response, failure_response
import time


def get(request):
    if not request.client.log_in:
        return failure_response({
            'error': {
                'description': 'You are not logged'
            }
        })

    timestamps = Setting.objects.filter(
        Q(key='start') | Q(key='end')
    )
    now = time.time()

    data = {}
    for timestamp in timestamps:
        diff = int(int(timestamp.value) -  now)

        data[timestamp.key] = diff if diff > 0 else 0


    return success_response(data)

def current(request):
    return success_response({
        'timestamp': int(time.time())
    })