from django.conf import settings
from django.apps import apps as django_apps
from edc_model_wrapper import ModelWrapper


class TbAdolConsentModelWrapper(ModelWrapper):

    model = 'flourish_caregiver.tbadolconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_dashboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier', 'first_name', 'last_name', 'initials',
                         'dob', 'identity', 'identity_type', 'language', 'is_dob_estimated',
                         'is_literate', 'witness_name', 'confirm_identity', 'citizen',
                         'adol_firstname', 'adol_lastname', 'adol_gender', 'adol_dob']
