from django.conf import settings
from edc_model_wrapper import ModelWrapper


class TbAdolScreeningModelWrapper(ModelWrapper):

    model = 'flourish_caregiver.tbadoleligibility'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    next_url_attrs = ['subject_identifier', 'screening_identifier']
    querystring_attrs = ['subject_identifier', 'screening_identifier']
