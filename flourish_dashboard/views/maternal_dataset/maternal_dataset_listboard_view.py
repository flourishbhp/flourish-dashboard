from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormMixin
import re

from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ...model_wrappers import LocatorWithLogEntryModelWrapper
from .filters import ListboardViewFilters
from ...forms import WorklistCreateListForm


class MaternalDatasetListBoardView(
        NavbarViewMixin, EdcBaseViewMixin,
        FormMixin, ListboardFilterViewMixin, SearchFormViewMixin,
        ListboardView):

    listboard_template = 'maternal_dataset_listboard_template'
    listboard_url = 'maternal_dataset_listboard_url'
    listboard_panel_style = 'info'
    listboard_fa_icon = "fa-user-plus"

    form_class = WorklistCreateListForm
    model = 'flourish_caregiver.maternaldataset'
    model_wrapper_cls = LocatorWithLogEntryModelWrapper
    listboard_view_filters = ListboardViewFilters()
    navbar_name = 'flourish_dashboard'
    navbar_selected_item = 'maternal_dataset'
    ordering = '-modified'
    paginate_by = 10
    search_form_url = 'maternal_dataset_listboard_url'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            maternal_locator_add_url=self.model_cls().get_absolute_url())
        return context

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get('screening_identifier'):
            options.update(
                {'screening_identifier': kwargs.get('screening_identifier')})
        return options

    def extra_search_options(self, search_term):
        q = Q()
        if re.match('^[A-Z]+$', search_term):
            q = Q(first_name__exact=search_term)
        return q
