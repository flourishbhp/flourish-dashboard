from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import YES

from .tb_adol_screening_model_wrapper import TbAdolScreeningModelWrapper


class TbAdolScreeningModelWrapperMixin:

    adol_screening_model_wrapper_cls = TbAdolScreeningModelWrapper

    @property
    def tb_adol_screening_model_obj(self):
        """Returns a tb adolescent screening model instance or None.
        """
        try:
            return self.tb_adol_screening_cls.objects.get(
                **self.tb_adol_screening_options)
        except ObjectDoesNotExist:
            return None

    @property
    def tb_adol_screening(self):
        """"Returns a wrapped saved or unsaved tb adolescent screening
        """
        model_obj = self.tb_adol_screening_model_obj or self.tb_adol_screening_cls(
            **self.create_tb_adol_screening_options)
        return TbAdolScreeningModelWrapper(model_obj=model_obj)

    @property
    def tb_adol_screening_cls(self):
        return django_apps.get_model('flourish_caregiver.tbadoleligibility')

    @property
    def tb_adol_eligibility(self):
        if self.tb_adol_screening_model_obj:
            return self.tb_adol_screening_model_obj.tb_adol_participation == YES

    @property
    def create_tb_adol_screening_options(self):
        """Returns a dictionary of options to create a new
        unpersisted tb adolescent screening model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            )
        return options

    @property
    def tb_adol_screening_options(self):
        """Returns a dictionary of options to get an existing
         tb adolescent screening model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            )
        return options
