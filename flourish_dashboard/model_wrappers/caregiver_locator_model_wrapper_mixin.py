from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .caregiver_locator_model_wrapper import CaregiverLocatorModelWrapper


class CaregiverLocatorModelWrapperMixin:

    locator_model_wrapper_cls = CaregiverLocatorModelWrapper

    @property
    def locator_model_obj(self):
        """Returns a caregiver locator model instance or None.
        """
        try:
            return self.caregiver_locator_cls.objects.get(
                **self.caregiver_locator_options)
        except ObjectDoesNotExist:
            return None

    @property
    def caregiver_locator(self):
        """"Returns a wrapped saved or unsaved caregiver locator
        """
        model_obj = self.locator_model_obj or self.caregiver_locator_cls(
            **self.create_caregiver_locator_options)
        return CaregiverLocatorModelWrapper(model_obj=model_obj)

    @property
    def caregiver_locator_cls(self):
        return django_apps.get_model('flourish_caregiver.caregiverlocator')

    @property
    def create_caregiver_locator_options(self):
        """Returns a dictionary of options to create a new
        unpersisted caregiver locator model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier,)
        if self.study_maternal_identifier and getattr(self, 'study_maternal_identifier'):
            options.update({'study_maternal_identifier': self.study_maternal_identifier})
        if getattr(self, 'first_name'):
            options.update({'first_name': self.first_name, 'last_name': self.last_name})
        return options

    @property
    def caregiver_locator_options(self):
        """Returns a dictionary of options to get an existing
         caregiver locator model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier,)
        return options
