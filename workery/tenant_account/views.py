# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.staff import StaffFilter
from tenant_foundation.models import Staff


#----------#
# UPDATE #
#----------#


class AccountUpdateView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'staff'
    model = Staff
    template_name = 'tenant_account/update/view.html'
    menu_id = "profile"
