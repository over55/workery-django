# -*- coding: utf-8 -*-
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation import constants
from shared_foundation.mixins import (
    ExtraRequestProcessingMixin,
    GroupRequiredMixin,
    WorkeryTemplateView,
    WorkeryListView,
    WorkeryDetailView
)
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import (
    Associate,
    InsuranceRequirement,
    SkillSet,
    Tag
)


class MemberUpdateView(LoginRequiredMixin, GroupRequiredMixin, WorkeryDetailView):
    context_object_name = 'associate'
    model = Associate
    template_name = 'tenant_associate/update/view.html'
    menu_id = "associates"
    group_required = [
        constants.EXECUTIVE_GROUP_ID,
        constants.MANAGEMENT_GROUP_ID,
        constants.FRONTLINE_GROUP_ID
    ]

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
        modified_context['insurance_requirements'] = InsuranceRequirement.objects.all()
        modified_context['tags'] = Tag.objects.all()
        modified_context['skill_sets'] = SkillSet.objects.all().order_by('sub_category')

        # Return our modified context.
        return modified_context
