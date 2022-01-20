from flourish_caregiver.models.subject_consent import SubjectConsent

from django.apps import apps as django_apps
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from edc_base.utils import get_uuid
from edc_consent import ConsentModelWrapperMixin
from edc_model_wrapper import ModelWrapper

from .antenatal_enrollment_wrapper_mixin import AntenatalEnrollmentModelWrapperMixin
from .bhp_prior_screening_model_wrapper_mixin import BHPPriorScreeningModelWrapperMixin
from .caregiver_locator_model_wrapper_mixin import CaregiverLocatorModelWrapperMixin
from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .flourish_consent_version_model_wrapper_mixin import FlourishConsentVersionModelWrapperMixin
from .subject_consent_model_wrapper import SubjectConsentModelWrapper


class MaternalScreeningModelWrapper(AntenatalEnrollmentModelWrapperMixin,
                                    CaregiverLocatorModelWrapperMixin,
                                    ConsentModelWrapperMixin,
                                    ChildAssentModelWrapperMixin,
                                    BHPPriorScreeningModelWrapperMixin,
                                    FlourishConsentVersionModelWrapperMixin,
                                    ModelWrapper):
    consent_model_wrapper_cls = SubjectConsentModelWrapper
    model = 'flourish_caregiver.screeningpregwomen'
    querystring_attrs = ['screening_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'maternal_screening_listboard_url')
    next_url_attrs = ['screening_identifier', 'subject_identifier', ]

    @property
    def consent_version_cls(self):
        return django_apps.get_model('flourish_caregiver.flourishconsentversion')

    @property
    def consent_version(self):
        version = '2'
        try:
            consent_version_obj = self.consent_version_cls.objects.get(
                screening_identifier=self.screening_identifier)
        except self.consent_version_cls.DoesNotExist:
            pass
        else:
            version = consent_version_obj.version
        return version

    @property
    def subject_identifier(self):
        if self.consent_model_obj:
            return self.consent_model_obj.subject_identifier
        return None

    @property
    def consent_model_obj(self):
        """Returns a consent model instance or None.
        """
        try:
            return self.subject_consent_cls.objects.get(**self.consent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def subject_consent_cls(self):
        return django_apps.get_model('flourish_caregiver.subjectconsent')

    @property
    def create_consent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted consent model instance.
        """
        options = dict(
            screening_identifier=self.screening_identifier,
            consent_identifier=get_uuid(),
            version=self.consent_version)
        return options

    @property
    def consent_options(self):
        """Returns a dictionary of options to get an existing
        consent model instance.
        """

        options = dict(
            screening_identifier=self.object.screening_identifier,
            version=self.consent_version)
        return options

    def is_eligible(self):
        return self.object.is_eligible

    def eligible_at_enrol(self):
        return self.object.is_eligible

    @property
    def create_caregiver_locator_options(self):
        """
        Override-(ed) the method to remove some of the fields not needed
        in this context

        Returns a dictionary of options to create a new
        (un)persisted caregiver locator model instance.
        """

        # Get the current screening identifier
        screening_identifier = self.object.screening_identifier
        # Get the subject identifier using the screening identifier after consent
        subject_identifier = SubjectConsent.objects.get(
            screening_identifier=screening_identifier,
            version=self.consent_version).subject_identifier,

        options = dict(
            screening_identifier=screening_identifier,
            subject_identifier=subject_identifier,
        )

        return options
