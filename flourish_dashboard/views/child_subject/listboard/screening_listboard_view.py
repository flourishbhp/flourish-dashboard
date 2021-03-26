import re

from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ....model_wrappers import CaregiverChildConsentModelWrapper


class ListboardView(EdcBaseViewMixin, NavbarViewMixin,
                    ListboardFilterViewMixin, SearchFormViewMixin,
                    ListboardView):

    listboard_template = 'child_screening_listboard_template'
    listboard_url = 'child_screening_listboard_url'
    listboard_panel_style = 'success'
    listboard_fa_icon = "far fa-user-circle"

    model = 'flourish_caregiver.caregiverchildconsent'
    model_wrapper_cls = CaregiverChildConsentModelWrapper
    navbar_name = 'flourish_dashboard'
    navbar_selected_item = 'child_screening'
    search_form_url = 'child_screening_listboard_url'

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get('screening_identifier'):
            options.update(
                {'subject_consent__screening_identifier': kwargs.get('screening_identifier')})
        return options

    def extra_search_options(self, search_term):
        q = Q()
        if re.match('^[A-Z]+$', search_term):
            q = Q(first_name__exact=search_term)
        return q
