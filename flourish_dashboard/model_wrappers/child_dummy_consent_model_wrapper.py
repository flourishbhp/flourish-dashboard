from django.conf import settings
from edc_model_wrapper import ModelWrapper

from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .child_birth_model_wrapper_mixin import ChildBirthModelWrapperMixin
from .child_death_report_model_wrapper_mixin import \
    ChildDeathReportModelWrapperMixin
from .child_dummy_consent_model_wrapper_mixin import \
    ChildDummyConsentModelWrapperMixin
from .child_offstudy_model_wrapper_mixin import ChildOffstudyModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin


class ChildDummyConsentModelWrapper(ChildDummyConsentModelWrapperMixin,
                                    ChildAssentModelWrapperMixin,
                                    ConsentModelWrapperMixin,
                                    ChildBirthModelWrapperMixin,
                                    ChildOffstudyModelWrapperMixin,
                                    ChildDeathReportModelWrapperMixin,
                                    ModelWrapper):
    model = 'flourish_child.childdummysubjectconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'child_listboard_url')
    next_url_attrs = ['subject_identifier', 'screening_identifier']
    querystring_attrs = ['subject_identifier', 'screening_identifier']
