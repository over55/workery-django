# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.order import OrderFilter
from tenant_foundation.models import Customer, Order, SkillSet


@method_decorator(login_required, name='dispatch')
class JobUpdateView(DetailView):
    context_object_name = 'job'
    model = Order
    template_name = 'tenant_order/update/view.html'

    def get_object(self):
        order = super().get_object()  # Call the superclass
        return order                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['search', 'summary', 'list']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Required for navigation
        modified_context['current_page'] = "jobs"

        # Set our skills
        modified_context['skillsets'] = SkillSet.objects.all()

        # Return our modified context.
        return modified_context
