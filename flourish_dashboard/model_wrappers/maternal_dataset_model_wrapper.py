from django.conf import settings

from edc_model_wrapper import ModelWrapper
from .maternal_screening_model_wrapper_mixin import MaternalScreeningModelWrapperMixin
from .maternal_locator_model_wrapper_mixin import MaternalLocatorModelWrapperMixin


class MaternalDatasetModelWrapper(MaternalLocatorModelWrapperMixin,
                                  MaternalScreeningModelWrapperMixin,
                                  ModelWrapper):

    model = 'flourish_maternal.maternaldataset'
    next_url_attrs = ['screening_identifier', 'subject_identifier', 'm_bid', 'bid']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_dataset_listboard_url')
    