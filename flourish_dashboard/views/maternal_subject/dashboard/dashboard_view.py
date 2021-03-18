from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from edc_base.view_mixins import EdcBaseViewMixin
from edc_dashboard.views import DashboardView as BaseDashboardView
from edc_data_manager.model_wrappers import DataActionItemModelWrapper
from edc_navbar import NavbarViewMixin
from edc_subject_dashboard.view_mixins import SubjectDashboardViewMixin


from ....model_wrappers import AppointmentModelWrapper, SubjectConsentModelWrapper
from ....model_wrappers import CaregiverLocatorModelWrapper, MaternalVisitModelWrapper
from ....model_wrappers import MaternalCrfModelWrapper, MaternalScreeningModelWrapper
from ....model_wrappers import CaregiverChildConsentModelWrapper


class DashboardView(EdcBaseViewMixin, SubjectDashboardViewMixin,
                    NavbarViewMixin, BaseDashboardView):

    dashboard_url = 'subject_dashboard_url'
    dashboard_template = 'subject_dashboard_template'
    appointment_model = 'edc_appointment.appointment'
    appointment_model_wrapper_cls = AppointmentModelWrapper
    crf_model_wrapper_cls = MaternalCrfModelWrapper
    consent_model = 'flourish_caregiver.subjectconsent'
    consent_model_wrapper_cls = SubjectConsentModelWrapper
    navbar_name = 'flourish_dashboard'
    visit_attr = 'maternalvisit'
    navbar_selected_item = 'consented_subject'
    subject_locator_model = 'flourish_caregiver.caregiverlocator'
    subject_locator_model_wrapper_cls = CaregiverLocatorModelWrapper
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

    @property
    def screening_pregnant_women(self):
        """Return a wrapped screening for preg women obj.
        """
        screening_cls = django_apps.get_model('flourish_caregiver.screeningpregwomen')
        try:
            subject_screening = screening_cls.objects.get(
                screening_identifier=self.consent_wrapped.screening_identifier)
        except screening_cls.DoesNotExist:
            raise ValidationError('Subject Screening must exist.')
        else:
            return MaternalScreeningModelWrapper(subject_screening)

    @property
    def caregiver_child_consents(self):
        wrapped_assents = []
        child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')
        child_consents = child_consent_cls.objects.filter(
            subject_identifier__istartswith=self.subject_identifier)
        for child_consent in child_consents:
            wrapped_assents.append(CaregiverChildConsentModelWrapper(child_consent))
        return wrapped_assents

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            subject_consent=self.consent_wrapped,
            screening_preg_women=self.screening_pregnant_women,
            caregiver_child_consents=self.caregiver_child_consents)
        return context

    def set_current_schedule(self, onschedule_model_obj=None,
                             schedule=None, visit_schedule=None,
                             is_onschedule=True):
        if onschedule_model_obj:
            if is_onschedule:
                self.current_schedule = schedule
                self.current_visit_schedule = visit_schedule
                self.current_onschedule_model = onschedule_model_obj
            self.onschedule_models.append(onschedule_model_obj)
            self.visit_schedules.update(
                {visit_schedule.name: visit_schedule})

    def get_onschedule_model_obj(self, schedule):
        try:
            return schedule.onschedule_model_cls.objects.get(
                subject_identifier=self.subject_identifier,
                schedule_name=schedule.name)
        except ObjectDoesNotExist:
            return None
