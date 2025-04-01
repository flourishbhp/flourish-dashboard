from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_model_wrapper import ModelWrapper

from .caregiver_child_consent_model_wrapper_mixin import \
    CaregiverChildConsentModelWrapperMixin
from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .child_birth_model_wrapper_mixin import ChildBirthModelWrapperMixin
from .child_consent_version_model_wrapper_mixin import ChildConsentVersionModelWrapperMixin
from .child_continued_consent_model_wrapper_mixin import \
    ChildContinuedConsentModelWrapperMixin
from .child_death_report_model_wrapper_mixin import ChildDeathReportModelWrapperMixin
from .child_offstudy_model_wrapper_mixin import ChildOffstudyModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin
from .maternal_delivery_wrapper_mixin import MaternalDeliveryModelWrapperMixin
from .pre_flourish_birth_data_model_wrapper_mixin import \
    PreFlourishBirthDataModelWrapperMixin
from .tb_adol_assent_model_wrapper_mixin import TbAdolChildAssentModelWrapperMixin
from .tb_adol_offstudy_model_wrapper_mixin import TbAdolOffstudyModelWrapperMixin
from .missed_birth_visit_model_wrapper_mixin import MissedBirthVisitModelWrapperMixin


class CaregiverChildConsentModelWrapper(CaregiverChildConsentModelWrapperMixin,
                                        TbAdolChildAssentModelWrapperMixin,
                                        ConsentModelWrapperMixin,
                                        ChildAssentModelWrapperMixin,
                                        ChildConsentVersionModelWrapperMixin,
                                        ChildContinuedConsentModelWrapperMixin,
                                        ChildBirthModelWrapperMixin,
                                        MaternalDeliveryModelWrapperMixin,
                                        ChildDeathReportModelWrapperMixin,
                                        ChildOffstudyModelWrapperMixin,
                                        TbAdolOffstudyModelWrapperMixin,
                                        PreFlourishBirthDataModelWrapperMixin,
                                        MissedBirthVisitModelWrapperMixin,
                                        ModelWrapper):
    model = 'flourish_caregiver.caregiverchildconsent'
    querystring_attrs = ['subject_consent', 'subject_identifier']
    next_url_attrs = ['subject_consent', 'subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_listboard_url')

    @property
    def consent_options(self):
        """Returns a dictionary of options to get an existing
        consent model instance.
        """
        options = dict(
            screening_identifier=self.screening_identifier,
            version=self.consent_version)
        return options

    @property
    def screening_identifier(self):
        return self.object.subject_consent.screening_identifier

    @property
    def maternal_delivery_model_obj(self):
        """Returns a maternal delivery model instance or None.
        """
        try:
            return self.maternal_delivery_cls.objects.get(
                child_subject_identifier=self.object.subject_identifier)
        except ObjectDoesNotExist:
            return None
