from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .maternal_locator_model_wrapper_mixin import MaternalLocatorModelWrapperMixin


class SubjectConsentModelWrapper(MaternalLocatorModelWrapperMixin, ModelWrapper):

    model = 'flourish_maternal.subjectconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'maternal_screening_listboard_url')
    next_url_attrs = ['screening_identifier']
    querystring_attrs = ['screening_identifier', 'subject_identifier']
