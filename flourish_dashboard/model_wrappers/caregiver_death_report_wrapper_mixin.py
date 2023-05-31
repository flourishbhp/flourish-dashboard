from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from flourish_dashboard.model_wrappers.death_report_model_wrapper import \
    CaregiverOffstudyModelWrapper


class CaregiverOffstudyModelWrapperMixin:

    caregiver_death_report_model_wrapper_cls = CaregiverOffstudyModelWrapper

    @property
    def caregiver_death_report_model_obj(self):
        """Returns a caregiver death report model instance or None.
        """
        try:
            return self.caregiver_death_report_cls.objects.get(
                **self.caregiver_death_report_options)
        except ObjectDoesNotExist:
            return None

    @property
    def caregiver_death_report(self):
        """Returns a wrapped saved or unsaved caregiver death report.
        """
        model_obj = self.caregiver_death_report_model_obj or self.caregiver_death_report_cls(
            **self.create_caregiver_death_report_options)
        return self.caregiver_death_report_model_wrapper_cls(model_obj=model_obj)

    @property
    def caregiver_death_report_cls(self):
        return django_apps.get_model('flourish_prn.caregiverdeathreport')

    @property
    def create_caregiver_death_report_options(self):
        """Returns a dictionary of options to create a new
        unpersisted caregiver death report model instance.
        """
        options = dict(
            subject_identifier=self.consent.subject_identifier,
            )
        return options

    @property
    def caregiver_death_report_options(self):
        """Returns a dictionary of options to get an existing
        caregiver death report model instance.
        """
        options = dict(
            subject_identifier=self.consent.subject_identifier)
        return options

    @property
    def show_dashboard(self):
        return True
