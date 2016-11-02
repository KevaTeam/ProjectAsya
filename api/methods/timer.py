from django.db.models import Q
from api.models import Setting
from api.helpers import success_response
import time


def get(request):
    timestamps = Setting.objects.filter(
        Q(key='start') | Q(key='end')
    )
    now = time.time()

    data = {}
    for timestamp in timestamps:
        diff = int(int(timestamp.value) -  now)

        data[timestamp.key] = diff if diff > 0 else 0


    return success_response(data)