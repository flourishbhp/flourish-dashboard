from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .subject_consent_model_wrapper_mixin import SubjectConsentModelWrapperMixin

class MaternalScreeningModelWrapper(SubjectConsentModelWrapperMixin,
                                    ModelWrapper):

    model = 'flourish_maternal.subjectscreening'
    querystring_attrs = ['screening_identifier']
    next_url_attrs = ['screening_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_screening_listboard_url')
