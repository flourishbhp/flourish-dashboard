import re

from django.apps import apps as django_apps
from django.db.models import Q
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.view_mixins import ListboardFilterViewMixin, SearchFormViewMixin
from edc_dashboard.views import ListboardView
from edc_navbar import NavbarViewMixin

from ....model_wrappers import SubjectConsentModelWrapper


class ListboardView(EdcBaseViewMixin, NavbarViewMixin,
                    ListboardFilterViewMixin, SearchFormViewMixin,
                    ListboardView):
    listboard_template = 'subject_listboard_template'
    listboard_url = 'subject_listboard_url'
    listboard_panel_style = 'success'
    listboard_fa_icon = "far fa-user-circle"

    model = 'flourish_caregiver.subjectconsent'
    model_wrapper_cls = SubjectConsentModelWrapper
    navbar_name = 'flourish_dashboard'
    navbar_selected_item = 'consented_subject'
    search_form_url = 'subject_listboard_url'

    def get_queryset_filter_options(self, request, *args, **kwargs):
        options = super().get_queryset_filter_options(request, *args, **kwargs)
        if kwargs.get('subject_identifier'):
            options.update(
                {'subject_identifier': kwargs.get('subject_identifier')})
        return options

    def extra_search_options(self, search_term):
        q = Q()
        if re.match('^[A-Z]+$', search_term):
            q = Q(first_name__contains=search_term)
        return q

    @property
    def consent_version_cls(self):
        return django_apps.get_model('flourish_caregiver.flourishconsentversion')

    def consent_version(self, screening_identifier):
        version = '1'
        try:
            consent_version_obj = self.consent_version_cls.objects.get(
                screening_identifier=screening_identifier)
        except self.consent_version_cls.DoesNotExist:
            pass
        else:
            version = consent_version_obj.version
        return version

    # def get_queryset(self):
    #     subjects = super().get_queryset()
    #     for subject in subjects:
    #         latest_consent_version = self.consent_version(subject.screening_identifier)
    #         if(latest_consent_version != subject.version):
    #             subjects = subjects.exclude(pk=subject.id)
    #     return subjects
