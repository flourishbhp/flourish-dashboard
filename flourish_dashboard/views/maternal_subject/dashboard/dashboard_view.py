from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.views import DashboardView as BaseDashboardView
from edc_data_manager.model_wrappers import DataActionItemModelWrapper
from edc_navbar import NavbarViewMixin
from edc_subject_dashboard.view_mixins import SubjectDashboardViewMixin


from ....model_wrappers import AppointmentModelWrapper, SubjectConsentModelWrapper
from ....model_wrappers import MaternalLocatorModelWrapper, MaternalVisitModelWrapper


class DashboardView(EdcBaseViewMixin, SubjectDashboardViewMixin,
                    NavbarViewMixin, BaseDashboardView):

    dashboard_url = 'subject_dashboard_url'
    dashboard_template = 'subject_dashboard_template'
    appointment_model = 'edc_appointment.appointment'
    appointment_model_wrapper_cls = AppointmentModelWrapper
    consent_model = 'flourish_caregiver.subjectconsent'
    consent_model_wrapper_cls = SubjectConsentModelWrapper
    navbar_name = 'flourish_dashboard'
    navbar_selected_item = 'consented_subject'
    subject_locator_model = 'flourish_caregiver.maternallocator'
    subject_locator_model_wrapper_cls = MaternalLocatorModelWrapper
    visit_model_wrapper_cls = MaternalVisitModelWrapper
    special_forms_include_value = 'flourish_dashboard/maternal_subject/dashboard/special_forms.html'
    data_action_item_template = 'flourish_dashboard/maternal_subject/dashboard/data_manager.html'

    @property
    def appointments(self):
        """Returns a Queryset of all appointments for this subject.
        """
        if not self._appointments:
            self._appointments = self.appointment_model_cls.objects.filter(
                subject_identifier=self.subject_identifier).order_by(
                    'visit_code')
        return self._appointments

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            subject_consent=self.consent_wrapped, )
        return context
