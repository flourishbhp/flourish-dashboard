from django.conf import settings

from edc_model_wrapper import ModelWrapper


class CaregiverLocatorModelWrapper(ModelWrapper):
    model = 'flourish_caregiver.caregiverlocator'
    querystring_attrs = ['screening_identifier', 'subject_identifier',
                         'study_maternal_identifier', 'first_name', 'last_name']
    next_url_attrs = ['subject_identifier', ]
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')
