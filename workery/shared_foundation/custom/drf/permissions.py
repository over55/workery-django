from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions


class IsAuthenticatedAndIsActivePermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint because your account is suspended.')

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_active

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return request.user.is_active

        return False
