from django.conf import settings

from edc_model_wrapper import ModelWrapper
from .maternal_screening_model_wrapper_mixin import MaternalScreeningModelWrapperMixin
from .caregiver_locator_model_wrapper_mixin import CaregiverLocatorModelWrapperMixin

from flourish_caregiver.models import LocatorLog
from .locator_log_model_wrapper import LocatorLogModelWrapper


class MaternalDatasetModelWrapper(CaregiverLocatorModelWrapperMixin,
                                  MaternalScreeningModelWrapperMixin,
                                  ModelWrapper):

    model = 'flourish_caregiver.maternaldataset'
    querystring_attrs = [
        'screening_identifier', 'subject_identifier',
        'study_maternal_identifier', 'study_child_identifier']
    next_url_attrs = [
        'screening_identifier', 'subject_identifier',
        'study_maternal_identifier', 'study_child_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_dataset_listboard_url')

    # @property
    # def log_entries(self):
    #     locator_log = getattr(self.object, 'maternal_dataset')
    #     wrapped_entries = []
    #     log_entries = LocatorLog.objects.filter(
    #         locator_log=locator_log)
    #     for log_entry in log_entries:
    #         wrapped_entries.append(
    #             LocatorLogEntryModelWrapper(log_entry))
    #
    #     return wrapped_entries

    @property
    def locator_exists(self):
        exists = False
        log = LocatorLog.objects.get(
            maternal_dataset=self.object)
        if log.log_status == 'exist':
            return True
        return exists

    @property
    def log_entry(self):
        log_entry = LocatorLog(maternal_dataset=self.object)
        return LocatorLogModelWrapper(log_entry)
