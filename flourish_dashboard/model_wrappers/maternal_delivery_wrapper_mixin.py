from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .maternal_delivery_model_wrapper import MaternalDeliveryModelWrapper


class MaternalDeliveryModelWrapperMixin:

    maternal_delivery_model_wrapper_cls = MaternalDeliveryModelWrapper

    @property
    def maternal_delivery_model_obj(self):
        """Returns a maternal delivery model instance or None.
        """
        try:
            return self.maternal_delivery_cls.objects.get(**self.maternal_delivery_options)
        except ObjectDoesNotExist:
            return None

    @property
    def maternal_delivery(self):
        """Returns a wrapped saved or unsaved maternal del.
        """
        model_obj = self.maternal_delivery_model_obj or self.maternal_delivery_cls(
            **self.create_maternal_delivery_options)
        return self.maternal_delivery_model_wrapper_cls(model_obj=model_obj)

    @property
    def maternal_delivery_cls(self):
        return django_apps.get_model('flourish_caregiver.maternaldelivery')

    @property
    def create_maternal_delivery_options(self):
        """Returns a dictionary of options to create a new
        unpersisted maternal delivery model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier)
        return options

    @property
    def maternal_delivery_options(self):
        """Returns a dictionary of options to get an existing
        maternal delivery model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier)
        return options

    @property
    def maternal_ultrasound_initial_obj(self):
        ultrasound_initial_cls = django_apps.get_model(
            'flourish_caregiver.ultrasound')
        try:
            return ultrasound_initial_cls.objects.get(
                maternal_visit__subject_identifier=self.object.subject_identifier)
        except ObjectDoesNotExist:
            return None
