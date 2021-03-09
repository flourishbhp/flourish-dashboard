from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .caregiver_locator_model_wrapper_mixin import CaregiverLocatorModelWrapperMixin


class SubjectConsentModelWrapper(CaregiverLocatorModelWrapperMixin, ModelWrapper):

    model = 'flourish_caregiver.subjectconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'maternal_dataset_listboard_url')
    next_url_attrs = ['screening_identifier']
    querystring_attrs = ['screening_identifier', 'subject_identifier']
