from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin


class CaregiverEnrolmentInfoModelWrapper(ConsentModelWrapperMixin,
                                         ChildAssentModelWrapperMixin,
                                         ModelWrapper):

    model = 'flourish_caregiver.caregiverpreviouslyenrolled'
    querystring_attrs = ['subject_identifier']
    next_url_attrs = ['subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_listboard_url')
