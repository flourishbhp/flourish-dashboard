from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .caregiver_enrolment_info_model_wrapper import CaregiverEnrolmentInfoModelWrapper


class CaregiverEnrolmentInfoModelWrapperMixin:

    caregiver_enrolment_info_model_wrapper_cls = CaregiverEnrolmentInfoModelWrapper

    @property
    def caregiver_enrolment_info_cls(self):
        return django_apps.get_model(
            'flourish_caregiver.caregiverpreviouslyenrolled')

    @property
    def caregiver_enrolment_info_obj(self):
        """Returns a caregiver enrolment info model instance or None.
        """
        try:
            return self.caregiver_enrolment_info_cls.objects.get(
                **self.caregiver_enrolment_info_options)
        except ObjectDoesNotExist:
            return None

    @property
    def caregiver_enrolment_info(self):
        """"Returns a wrapped saved or unsaved caregiver enrolment info
        """
        model_obj = self.caregiver_enrolment_info_obj or self.caregiver_enrolment_info_cls(
            **self.create_caregiver_enrolment_info_options)
        return self.caregiver_enrolment_info_model_wrapper_cls(model_obj=model_obj)

    @property
    def create_caregiver_enrolment_info_options(self):
        """Returns a dictionary of options to create a new
        unpersisted caregiver enrolment info model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier,)
        return options

    @property
    def caregiver_enrolment_info_options(self):
        """Returns a dictionary of options to get an existing
         caregiver enrolment info model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier,)
        return options
