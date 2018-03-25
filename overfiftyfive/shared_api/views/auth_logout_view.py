from django.contrib.auth import authenticate, login, logout
from django.db import connection # Used for django tenants.
from rest_framework import permissions, status, response, views
from rest_framework.authtoken.models import Token


class LogoutAPIView(views.APIView):
    permission_classes = [permissions.IsAuthenticated,]

    def post(self, request):
        # Step 1: Delete the "auth_token" so our RESTFul API won't have a key.
        Token.objects.filter(user=request.user).delete()

        # RESET ALL THE USER PROFILE INFORMATION TO A SESSION.
        request.session['me_token_key'] = None
        request.session['me_schema_name'] = None

        # Step 2: Close the Django session.
        logout(request)

        # Step 3: Return success message.
        return response.Response(status=status.HTTP_200_OK)
