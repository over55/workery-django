# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, FormView, UpdateView
from django.views.generic import DetailView, ListView, TemplateView
from django.utils.decorators import method_decorator
from tenant_api.filters.associate import AssociateFilter
from tenant_foundation.models import Associate


@method_decorator(login_required, name='dispatch')
class AssociateListView(ListView):
    context_object_name = 'associate_list'
    queryset = Associate.objects.order_by('-created')
    template_name = 'tenant_associate/associate_list.html'
    paginate_by = 100

    # def head(self, *args, **kwargs):
    #     last_associate = self.get_queryset().latest('-last_modified')
    #     response = HttpResponse('')
    #     # RFC 1123 date format
    #     response['Last-Modified'] = last_associate.last_modified.strftime('%a, %d %b %Y %H:%M:%S GMT')
    #     return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "associates"
        return context

    def get_queryset(self):
        """
        Override the default queryset to allow dynamic filtering with
        GET parameterss using the 'django-filter' library.
        """
        queryset = None

        # The following code will use the native 'PostgreSQL' library
        # which comes with Django to utilize the 'full text search' feature.
        # For more details please read:
        # https://docs.djangoproject.com/en/2.0/ref/contrib/postgres/search/
        keyword = self.request.GET.get('keyword', None)
        if keyword:
            queryset = Associate.objects.full_text_search(keyword)
            queryset = queryset.order_by('-created')
        else:
            queryset = super(AssociateListView, self).get_queryset()

        # The following code will use the 'django-filter'
        filter = AssociateFilter(self.request.GET, queryset=queryset)
        queryset = filter.qs
        return queryset

@method_decorator(login_required, name='dispatch')
class AssociateSearchView(TemplateView):
    template_name = 'tenant_associate/associate_search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "associates"
        return context


@method_decorator(login_required, name='dispatch')
class AssociateCreateView(TemplateView):
    template_name = 'tenant_associate/associate_create.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "associates"
        return context


@method_decorator(login_required, name='dispatch')
class AssociateDetailView(DetailView):
    model = Associate
    template_name = 'tenant_associate/associate_detail.html'

    def get_object(self):
        associate = super().get_object()  # Call the superclass
        return associate  # Return the object

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_page'] = "associates"
        return context
