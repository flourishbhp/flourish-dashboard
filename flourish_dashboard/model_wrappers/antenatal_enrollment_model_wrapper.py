from django.conf import settings

from edc_model_wrapper import ModelWrapper


class AntenatalEnrollmentModelWrapper(ModelWrapper):

    model = 'flourish_caregiver.antenatalenrollment'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'maternal_screening_listboard_url')
    next_url_attrs = ['screening_identifier']
    querystring_attrs = ['subject_identifier', 'child_subject_identifier']
