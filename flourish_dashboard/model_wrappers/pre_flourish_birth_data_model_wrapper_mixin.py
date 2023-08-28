from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from flourish_dashboard.model_wrappers.pre_flourish_birth_data_model_wrapper import \
    PreFlourishBirthDataModelWrapper


class PreFlourishBirthDataModelWrapperMixin:
    pf_birth_data_model_wrapper_cls = PreFlourishBirthDataModelWrapper

    @property
    def pf_birth_data_model_obj(self):
        """Returns a tb pf_birth_data model instance or None.
        """
        try:
            return self.pf_birth_data_cls.objects.get(
                **self.pf_birth_data_options)
        except ObjectDoesNotExist:
            return None

    @property
    def pf_birth_data(self):
        """"Returns a wrapped saved or unsaved tb pf_birth_data
        """
        model_obj = self.pf_birth_data_model_obj or self.pf_birth_data_cls(
            **self.create_pf_birth_data_options)
        return self.pf_birth_data_model_wrapper_cls(model_obj=model_obj)

    @property
    def pf_birth_data_cls(self):
        return django_apps.get_model(self.pf_birth_data_model_wrapper_cls.model)

    @property
    def create_pf_birth_data_options(self):
        """Returns a dictionary of options to create a new
        unpersisted tb pf_birth_data model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
        )
        return options

    @property
    def pf_birth_data_options(self):
        """Returns a dictionary of options to get an existing
         tb pf_birth_data model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
        )
        return options
