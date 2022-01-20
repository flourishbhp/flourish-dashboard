from django.conf import settings
from edc_model_wrapper import ModelWrapper


class FlourishConsentVersionModelWrapper(ModelWrapper):

    model = 'flourish_caregiver.flourishconsentversion'
    visit_model_attr = 'subject_visit'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'maternal_screening_listboard_url')
    next_url_attrs = ['screening_identifier']
    querystring_attrs = ['screening_identifier', visit_model_attr]
