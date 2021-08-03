from django.apps import apps as django_apps
from django.conf import settings
from edc_model_wrapper import ModelWrapper
from itertools import chain

from .caregiver_contact_model_wrapper_mixin import CaregiverContactModelWrapperMixin
from .caregiver_enrolment_info_model_wrapper_mixin import CaregiverEnrolmentInfoModelWrapperMixin
from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .caregiver_locator_model_wrapper_mixin import CaregiverLocatorModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin
from .antenatal_enrollment_wrapper_mixin import AntenatalEnrollmentModelWrapperMixin
from .bhp_prior_screening_model_wrapper_mixin import BHPPriorScreeningModelWrapperMixin


class SubjectConsentModelWrapper(CaregiverContactModelWrapperMixin,
                                 ChildAssentModelWrapperMixin,
                                 CaregiverEnrolmentInfoModelWrapperMixin,
                                 CaregiverLocatorModelWrapperMixin,
                                 ConsentModelWrapperMixin,
                                 BHPPriorScreeningModelWrapperMixin,
                                 AntenatalEnrollmentModelWrapperMixin,
                                 ModelWrapper):

    model = 'flourish_caregiver.subjectconsent'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_listboard_url')
    next_url_attrs = ['subject_identifier', ]
    querystring_attrs = ['screening_identifier', 'subject_identifier',
                         'first_name', 'last_name', 'initials', 'gender',
                         'study_maternal_identifier', ]

    @property
    def study_maternal_identifier(self):
        if getattr(self, 'bhp_prior_screening_model_obj', None):
            return self.bhp_prior_screening_model_obj.study_maternal_identifier
        return ''

    @property
    def gender(self):
        return self.object.gender

    @property
    def create_caregiver_locator_options(self):
        """Returns a dictionary of options to create a new
        unpersisted caregiver locator model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier,)
        if self.assent_model_obj:
            options.update(
                {'study_maternal_identifier': self.assent_model_obj.study_maternal_identifier})
        else:
            options.update(
                {'subject_identifier': self.subject_identifier})
        if getattr(self, 'first_name'):
            options.update({'first_name': self.first_name, 'last_name': self.last_name})
        return options

    @property
    def overall_ineligible(self):
        return list(chain(self.assents_ineligible, self.children_ineligible))

    def is_pregnant(self):
        screening_preg_cls = django_apps.get_model('flourish_caregiver.screeningpregwomen')

        if self.consent_model_obj:
            try:
                screening_preg_cls.objects.get(
                    screening_identifier=self.consent_model_obj.screening_identifier)
            except screening_preg_cls.DoesNotExist:
                return False
            else:
                delivery_cls = django_apps.get_model('flourish_caregiver.maternaldelivery')
                try:
                    delivery_cls.objects.get(
                        subject_identifier=self.consent_model_obj.subject_identifier)
                except delivery_cls.DoesNotExist:
                    return True
                else:
                    return False
            return True
