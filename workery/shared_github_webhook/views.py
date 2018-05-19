
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
    """
    https://gist.github.com/vitorfs/145a8b8f0865cb65ee915e0c846fc303
    """
    # Verify if request came from GitHub
    # forwarded_for = u'{}'.format(request.META.get('HTTP_X_FORWARDED_FOR'))
    # client_ip_address = ip_address(forwarded_for)
    # whitelist = requests.get('https://api.github.com/meta').json()['hooks']

    # for valid_ip in whitelist:
    #     if client_ip_address in ip_network(valid_ip):
    #         break
    # else:
    #     return HttpResponseForbidden('Permission denied.')

    # Verify the request signature
    header_signature = request.META.get('HTTP_X_HUB_SIGNATURE')
    if header_signature is None:
        return HttpResponseForbidden('Permission denied.')

    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return HttpResponseServerError('Operation not supported.', status=501)

    mac = hmac.new(force_bytes(settings.O55_GITHUB_WEBHOOK_SECRET), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return HttpResponseForbidden('Permission denied.')

    # If request reached this point we are in a good shape
    # Process the GitHub events
    event = request.META.get('HTTP_X_GITHUB_EVENT', 'ping')

    if event == 'ping':
        return HttpResponse('pong')
    elif event == 'push':
        print("##############")
        print("#### PUSH ####")
        print("##############")

        import subprocess
        res = subprocess.call("redeploy.sh", shell=True)
        for line in res.splitlines():
            # process the output line by line
            print(line)

        print("##############")
        print("")

        # Deploy some code for example
        return HttpResponse('success')

    # In case we receive an event that's not ping or push
    return HttpResponse(status=204)
