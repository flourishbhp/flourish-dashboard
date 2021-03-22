from django.conf import settings
from django.db.models import Q
from edc_model_wrapper import ModelWrapper
from flourish_caregiver.models import LocatorLogEntry
from flourish_follow.models import LogEntry, InPersonContactAttempt

from .bhp_prior_screening_model_wrapper_mixin import BHPPriorScreeningModelWrapperMixin
from .caregiver_locator_model_wrapper_mixin import CaregiverLocatorModelWrapperMixin
from .child_assent_model_wrapper_mixin import ChildAssentModelWrapperMixin
from .consent_model_wrapper_mixin import ConsentModelWrapperMixin
from .locator_log_entry_model_wrapper import LocatorLogEntryModelWrapper
from .subject_consent_model_wrapper import SubjectConsentModelWrapper


class MaternalDatasetModelWrapper(ConsentModelWrapperMixin,
                                  CaregiverLocatorModelWrapperMixin,
                                  BHPPriorScreeningModelWrapperMixin,
                                  ChildAssentModelWrapperMixin,
                                  ModelWrapper):

    consent_model_wrapper_cls = SubjectConsentModelWrapper
    model = 'flourish_caregiver.maternaldataset'
    querystring_attrs = [
        'screening_identifier', 'subject_identifier',
        'study_maternal_identifier', 'study_child_identifier']
    next_url_attrs = ['study_maternal_identifier', 'screening_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_dataset_listboard_url')

    @property
    def log_entries(self):
        locator_log = getattr(self.object, 'locatorlog')
        wrapped_entries = []
        log_entries = LocatorLogEntry.objects.filter(
            locator_log=locator_log)
        for log_entry in log_entries:
            wrapped_entries.append(
                LocatorLogEntryModelWrapper(log_entry))

        return wrapped_entries

    @property
    def call_or_home_visit_success(self):
        """Returns true if the call or home visit was a success.
        """
        log_entries = LogEntry.objects.filter(
            ~Q(phone_num_success='none_of_the_above'),
            study_maternal_identifier=self.object.study_maternal_identifier,
            phone_num_success__isnull=False)
        home_visit_logs = InPersonContactAttempt.objects.filter(
            ~Q(successful_location='none_of_the_above'),
            study_maternal_identifier=self.object.study_maternal_identifier,
            successful_location__isnull=False)
        if log_entries:
            return True
        elif home_visit_logs:
            return True
        return False

    @property
    def locator_exists(self):
        locator_log = getattr(self.object, 'locatorlog')
        exists = False
        if LocatorLogEntry.objects.filter(locator_log=locator_log, log_status='exist'):
            exists = True
        return exists

    @property
    def log_entry(self):
        locator_log = getattr(self.object, 'locatorlog')
        log_entry = LocatorLogEntry(locator_log=locator_log)
        return LocatorLogEntryModelWrapper(log_entry)

    @property
    def contact_attempts(self):
        return False

    @property
    def screening_report_datetime(self):
        if self.bhp_prior_screening_model_obj:
            return self.bhp_prior_screening_model_obj.report_datetime

    def set_initials(self, first_name, last_name):
        initials = ''
        if (len(first_name.split(' ')) > 1):
            first = first_name.split(' ')[0]
            middle = first_name.split(' ')[1]
            initials = f'{first[:1]}{middle[:1]}{last_name[:1]}'
        else:
            initials = f'{first_name[:1]}{last_name[:1]}'
        return initials
