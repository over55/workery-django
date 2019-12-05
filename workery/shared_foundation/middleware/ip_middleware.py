from ipware import get_client_ip


class IPMiddleware:
    """
    Middleware responsible for attaching the user's IP address to each
    request made to our system.

    This middleware is dependent on the ``django-ipware`` library to work.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        client_ip, is_routable = get_client_ip(request)
        request.client_ip = client_ip
        request.client_ip_is_routable = is_routable

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
