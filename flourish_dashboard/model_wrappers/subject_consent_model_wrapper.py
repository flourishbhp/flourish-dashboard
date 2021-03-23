from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .caregiver_locator_model_wrapper_mixin import CaregiverLocatorModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin
from .antenatal_enrollment_wrapper_mixin import AntenatalEnrollmentModelWrapperMixin


class SubjectConsentModelWrapper(ChildAssentModelWrapperMixin,
                                 CaregiverLocatorModelWrapperMixin,
                                 ConsentModelWrapperMixin,
                                 AntenatalEnrollmentModelWrapperMixin,
                                 ModelWrapper):

    model = 'flourish_caregiver.subjectconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_listboard_url')
    next_url_attrs = ['subject_identifier', ]
    querystring_attrs = ['screening_identifier', 'subject_identifier',
                         'first_name', 'last_name', 'initials', 'gender']
