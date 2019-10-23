from django.contrib.auth.models import Group, Permission
from django.utils.translation import ugettext_lazy as _
from rest_framework import permissions
from shared_foundation.utils import has_permission


class CanListCreateTaskItemPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_permission(self, request, view):
        # print("has_permission", request.method)  # For debugging purposes only.

        # --- LIST ---
        if "GET" in request.method:
            return has_permission('can_get_task_item', request.user, request.user.groups.all())

        # --- CREATE ---
        if "POST" in request.method:
            return has_permission('can_post_task_item', request.user, request.user.groups.all())

        return False


class CanRetrieveUpdateDestroyTaskItemPermission(permissions.BasePermission):
    message = _('You do not have permission to access this API-endpoint.')

    def has_object_permission(self, request, view, obj):
        # print("has_object_permission", request.method)  # For debugging purposes only.

        # --- RETRIEVE ---
        if "GET" in request.method:
            # OWNERSHIP BASED
            if obj.job.associate:
                if request.user == obj.job.associate.owner:
                    return True

            # PERMISSION BASED
            return has_permission('can_get_task_items', request.user, request.user.groups.all())

        # ---UPDATE ---
        if "PUT" in request.method:
            # OWNERSHIP BASED
            if obj.job.associate:
                if request.user == obj.job.associate.owner:
                    return True

            # PERMISSION BASED
            return has_permission('can_put_task_item', request.user, request.user.groups.all())

        # --- DELETE ---
        if "DELETE" in request.method:
            # PERMISSION BASED
            return has_permission('can_delete_task_item', request.user, request.user.groups.all())

        return False
