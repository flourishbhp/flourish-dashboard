from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .maternal_screening_model_wrapper_mixin import \
    MaternalScreeningModelWrapperMixin


class MaternalScreeningModelWrapper(MaternalScreeningModelWrapperMixin,
                                    ModelWrapper):

    model = 'flourish_maternal.subjectscreening'
    querystring_attrs = ['screening_identifier']
    next_url_attrs = ['screening_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_screening_listboard_url')

    @property
    def maternal_screening(self):
        """"Returns a wrapped saved or unsaved maternal screening
        """
        model_obj = self.maternal_model_obj or self.maternal_screening_cls(
            **self.maternal_screening_options)
        return MaternalScreeningModelWrapper(model_obj=model_obj)
