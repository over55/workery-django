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
from tenant_foundation.models import (
    Staff,
    SkillSet,
    Tag
)


class LaunchpadView(LoginRequiredMixin, WorkeryTemplateView):
    template_name = 'tenant_setting/launchpad/view.html'
    menu_id = "settings"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tags'] = Tag.objects.all()
        context['skill_sets'] = SkillSet.objects.all()
        return context
