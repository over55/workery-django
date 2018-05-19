
import hmac
from hashlib import sha1

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.encoding import force_bytes

import requests
# from ipaddress import ip_address, ip_network

from django.views.decorators.csrf import csrf_exempt

@require_POST
@csrf_exempt
def github_webhook_handler(request):
    print("######## github_webhook_handler #######")
    return HttpResponse('pong')
