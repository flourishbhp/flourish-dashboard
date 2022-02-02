from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .caregiver_offstudy_model_wrapper import CaregiverOffstudyModelWrapper


class CaregiverOffstudyModelWrapperMixin:
    caregiver_offstudy_model_wrapper_cls = CaregiverOffstudyModelWrapper

    @property
    def caregiver_offstudy_obj(self):
        """Returns a caregiver offstudy model instance or None.
        """
        try:
            return self.caregiver_offstudy_cls.objects.get(
                **self.caregiver_offstudy_options)
        except ObjectDoesNotExist:
            return None

    @property
    def caregiver_offstudy(self):
        """"Returns a wrapped saved or unsaved caregiver offstudy
        """
        model_obj = self.caregiver_offstudy_obj or self.caregiver_offstudy_cls(
            **self.create_caregiver_offstudy_options
        )
        return self.caregiver_offstudy_model_wrapper_cls(model_obj=model_obj)

    @property
    def caregiver_offstudy_cls(self):
        return django_apps.get_model('flourish_prn.caregiveroffstudy')

    @property
    def create_caregiver_offstudy_options(self):
        """Returns a dictionary of options to create a new
        unpersisted subject locator model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier)
        return options

    @property
    def caregiver_offstudy_options(self):
        """Returns a dictionary of options to get an existing
         caregiver offstudy model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier, )
        return options
