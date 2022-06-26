from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .tb_offstudy_model_wrapper import TbOffstudyModelWrapper


class TbOffstudyModelWrapperMixin:
    offstudy_model_wrapper_cls = TbOffstudyModelWrapper

    @property
    def tb_offstudy_model_obj(self):
        """Returns a tb offstudy model instance or None.
        """
        try:
            return self.tb_offstudy_cls.objects.get(
                **self.tb_offstudy_options)
        except ObjectDoesNotExist:
            return None

    @property
    def tb_offstudy(self):
        """"Returns a wrapped saved or unsaved tb offstudy
        """
        model_obj = self.tb_offstudy_model_obj or self.tb_offstudy_cls(
            **self.create_tb_offstudy_options)
        return self.offstudy_model_wrapper_cls(model_obj=model_obj)

    @property
    def tb_offstudy_cls(self):
        return django_apps.get_model('flourish_caregiver.tboffstudy')

    @property
    def create_tb_offstudy_options(self):
        """Returns a dictionary of options to create a new
        unpersisted tb offstudy model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
        )
        return options

    @property
    def tb_offstudy_options(self):
        """Returns a dictionary of options to get an existing
         tb offstudy model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
        )
        return options
