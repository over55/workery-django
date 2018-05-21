# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from shared_foundation.mixins import ExtraRequestProcessingMixin
from tenant_foundation.models import Order


@method_decorator(login_required, name='dispatch')
class UnpaidJobOrderListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    queryset = Order.objects.filter(invoice_service_fee_payment_date=None).order_by('-id')
    template_name = 'tenant_financial/list/unpaid_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "financials"

        # Get count of total tasks.
        modified_context['unpaid_count'] = Order.objects.filter(invoice_service_fee_payment_date=None).count()
        modified_context['paid_count'] = Order.objects.filter(~Q(invoice_service_fee_payment_date=None)).count()
        modified_context['all_count'] = Order.objects.all().count()

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class PaidJobOrderListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    queryset = Order.objects.filter(~Q(invoice_service_fee_payment_date=None)).order_by('-invoice_service_fee_payment_date')
    template_name = 'tenant_financial/list/paid_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "financials"

        # Get count of total tasks.
        modified_context['unpaid_count'] = Order.objects.filter(invoice_service_fee_payment_date=None).count()
        modified_context['paid_count'] = Order.objects.filter(~Q(invoice_service_fee_payment_date=None)).count()
        modified_context['all_count'] = Order.objects.all().count()

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class AllJobOrderListView(ListView, ExtraRequestProcessingMixin):
    context_object_name = 'job_list'
    queryset = Order.objects.all().order_by('-id')
    template_name = 'tenant_financial/list/all_view.html'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "financials"

        # Get count of total tasks.
        modified_context['unpaid_count'] = Order.objects.filter(invoice_service_fee_payment_date=None).count()
        modified_context['paid_count'] = Order.objects.filter(~Q(invoice_service_fee_payment_date=None)).count()
        modified_context['all_count'] = Order.objects.all().count()

        # DEVELOPERS NOTE:
        # - We will extract the URL parameters and save them into our context
        #   so we can use this to help the pagination.
        modified_context['parameters'] = self.get_params_dict([])

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class JobRetrieveView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job_item'
    model = Order
    template_name = 'tenant_financial/retrieve/view.html'

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['unpaid-jobs', 'paid-jobs', 'all-jobs']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context


@method_decorator(login_required, name='dispatch')
class JobUpdateView(DetailView, ExtraRequestProcessingMixin):
    context_object_name = 'job_item'
    model = Order
    template_name = 'tenant_financial/update/view.html'

    def get_object(self):
        obj = super().get_object()  # Call the superclass
        return obj                  # Return the object

    def get_context_data(self, **kwargs):
        # Get the context of this class based view.
        modified_context = super().get_context_data(**kwargs)

        # Required for navigation
        modified_context['current_page'] = "task"

        # Validate the template selected.
        template = self.kwargs['template']
        if template not in ['unpaid-jobs', 'paid-jobs', 'all-jobs']:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied(_('You entered wrong format.'))
        modified_context['template'] = template

        # Return our modified context.
        return modified_context
