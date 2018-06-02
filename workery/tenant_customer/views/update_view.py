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
from tenant_api.filters.customer import CustomerFilter
from tenant_foundation.models import (
    Customer,
    SkillSet,
    Tag
)


class CustomerUpdateView(LoginRequiredMixin, WorkeryDetailView):
    context_object_name = 'customer'
    model = Customer
    template_name = 'tenant_customer/update/view.html'
    menu_id = "customers"

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Extra
        modified_context['tags'] = Tag.objects.all()
        modified_context['skill_sets'] = SkillSet.objects.all()

        # Return our modified context.
        return modified_context
