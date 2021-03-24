from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .caregiver_child_consent_model_wrapper_mixin import CaregiverChildConsentModelWrapperMixin
from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin


class CaregiverChildConsentModelWrapper(CaregiverChildConsentModelWrapperMixin,
                                        ConsentModelWrapperMixin,
                                        ChildAssentModelWrapperMixin,
                                        ModelWrapper):

    model = 'flourish_caregiver.caregiverchildconsent'
    querystring_attrs = ['subject_consent', 'subject_identifier']
    next_url_attrs = ['subject_consent', 'subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_listboard_url')

    @property
    def screening_identifier(self):
        return self.object.subject_consent.screening_identifier

    @property
    def child_age(self):
        if self.object.child_age_at_enrollment:
            return self.object.child_age_at_enrollment
        return 0
