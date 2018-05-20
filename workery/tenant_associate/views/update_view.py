# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import (
    Associate,
    InsuranceRequirement,
    SkillSet,
    Tag
)


@method_decorator(login_required, name='dispatch')
class MemberUpdateView(DetailView):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/update/view.html'

    def get_object(self):
        associate = super().get_object()  # Call the superclass
        return associate                  # Return the object

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
        modified_context['current_page'] = "associates"

        # Extra
        modified_context['insurance_requirements'] = InsuranceRequirement.objects.all()
        modified_context['tags'] = Tag.objects.all()
        modified_context['skill_sets'] = SkillSet.objects.all()

        # Return our modified context.
        return modified_context
