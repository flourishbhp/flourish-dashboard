from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_model_wrapper import ModelWrapper

from .bhp_prior_screening_model_wrapper import BHPPriorScreeningModelWrapper


class BHPPriorScreeningModelWrapperMixin(ModelWrapper):

    prior_screening_model_wrapper_cls = BHPPriorScreeningModelWrapper

    @property
    def bhp_prior_screening_model_obj(self):
        """Returns a bhp prior model instance or None.
        """
        try:
            return self.bhp_prior_screening_cls.objects.get(
                **self.bhp_prior_screening_options)
        except ObjectDoesNotExist:
            return None

    @property
    def bhp_prior_screening(self):
        """"Returns a wrapped saved or unsaved bhp prior screening
        """
        model_obj = self.bhp_prior_screening_model_obj or self.bhp_prior_screening_cls(
            **self.create_bhp_prior_screening_options)
        return self.prior_screening_model_wrapper_cls(model_obj=model_obj)

    @property
    def bhp_prior_screening_cls(self):
        return django_apps.get_model(
            'flourish_caregiver.screeningpriorbhpparticipants')

    @property
    def create_bhp_prior_screening_options(self):
        """Returns a dictionary of options to create a new
        unpersisted bhp prior screening model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier,
            study_maternal_identifier=self.study_maternal_identifier)
        return options

    @property
    def bhp_prior_screening_options(self):
        """Returns a dictionary of options to get an existing
        maternal screening model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier)
        return options
