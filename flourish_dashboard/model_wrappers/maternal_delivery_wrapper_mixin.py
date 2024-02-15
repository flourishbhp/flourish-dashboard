from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .maternal_delivery_model_wrapper import MaternalDeliveryModelWrapper
from ..utils import flourish_dashboard_utils


class MaternalDeliveryModelWrapperMixin:
    maternal_delivery_model_wrapper_cls = MaternalDeliveryModelWrapper

    def maternal_delivery_model_obj(self, child_subject_identifier):
        """Returns a maternal delivery model instance or None.
        """
        try:
            return self.maternal_delivery_cls.objects.get(
                **self.maternal_delivery_options(child_subject_identifier))
        except ObjectDoesNotExist:
            return None

    @property
    def maternal_deliveries(self):
        """Returns a wrapped saved or unsaved maternal del.
        """
        wrapped_entries = []
        for maternal_delivery in self.maternal_ultrasound_initial_obj:
            if flourish_dashboard_utils.screening_object_by_child_pid(
                    self.consent.screening_identifier,
                    maternal_delivery.child_subject_identifier):
                model_obj = (self.maternal_delivery_model_obj(
                    maternal_delivery.child_subject_identifier) or
                             self.maternal_delivery_cls(
                                 **self.create_maternal_delivery_options(
                                     maternal_delivery.child_subject_identifier)))
                wrapped_entries.append(
                    self.maternal_delivery_model_wrapper_cls(model_obj))
        return wrapped_entries

    @property
    def maternal_delivery_cls(self):
        return django_apps.get_model('flourish_caregiver.maternaldelivery')

    def create_maternal_delivery_options(self, child_subject_identifier):
        """Returns a dictionary of options to create a new
        unpersisted maternal delivery model instance.
        """
        options = dict(
            child_subject_identifier=child_subject_identifier,
            subject_identifier=self.object.subject_identifier)
        return options

    def maternal_delivery_options(self, child_subject_identifier):
        """Returns a dictionary of options to get an existing
        maternal delivery model instance.
        """
        options = dict(
            child_subject_identifier=child_subject_identifier,
            subject_identifier=self.object.subject_identifier)
        return options

    @property
    def maternal_ultrasound_initial_obj(self):
        ultrasound_initial_cls = django_apps.get_model(
            'flourish_caregiver.ultrasound')
        return ultrasound_initial_cls.objects.filter(
            maternal_visit__subject_identifier=self.object.subject_identifier)
