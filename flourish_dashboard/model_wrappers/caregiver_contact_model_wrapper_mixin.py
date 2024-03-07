from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .caregiver_contact_model_wrapper import CaregiverContactModelWrapper


class CaregiverContactModelWrapperMixin:

    caregiver_contact_model_wrapper_cls = CaregiverContactModelWrapper

    @property
    def caregiver_contact_model_obj(self):
        """Returns a caregiver contact model instance or None.
        """
        try:
            return self.caregiver_contact_cls.objects.get(
                **self.caregiver_contact_options)
        except ObjectDoesNotExist:
            return None

    @property
    def caregiver_contact(self):
        """Returns a wrapped unsaved caregiver contact.
        """
        model_obj = self.caregiver_contact_cls(
            **self.create_caregiver_contact_options)
        return self.caregiver_contact_model_wrapper_cls(model_obj=model_obj)

    @property
    def caregiver_contact_cls(self):
        return django_apps.get_model('flourish_caregiver.caregivercontact')

    @property
    def create_caregiver_contact_options(self):
        """Returns a dictionary of options to create a new
        unpersisted caregiver contact model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            study_name='flourish')
        return options

    @property
    def caregiver_contact_options(self):
        """Returns a dictionary of options to get an existing
        caregiver contact model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier)
        return options
