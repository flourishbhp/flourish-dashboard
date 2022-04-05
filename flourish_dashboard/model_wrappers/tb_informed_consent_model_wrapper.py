from django.conf import settings
from edc_model_wrapper import ModelWrapper


class TbInformedConsentModelWrapper(ModelWrapper):
    model = 'flourish_caregiver.tbinformedconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier', 'first_name', 'last_name', 'initials',
                         'gender', 'dob', 'identity', 'identity_type', 'language',
                         'is_literate', 'witness_name']
