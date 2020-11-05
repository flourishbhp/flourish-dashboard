from django.conf import settings

from edc_model_wrapper import ModelWrapper
from .maternal_screening_model_wrapper_mixin import MaternalScreeningModelWrapperMixin
from .maternal_locator_model_wrapper_mixin import MaternalLocatorModelWrapperMixin

from flourish_caregiver.models import LocatorLogEntry
from .locator_log_entry_model_wrapper import LocatorLogEntryModelWrapper


class MaternalDatasetModelWrapper(MaternalLocatorModelWrapperMixin,
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
    def locator_exists(self):
        locator_log = getattr(self.object, 'locatorlog')
        exists = False
        log_entries = LocatorLogEntry.objects.filter(
            locator_log=locator_log)
        for log_entry in log_entries:
            if log_entry.log_status == 'exist':
                return True
        return exists

    @property
    def log_entry(self):
        locator_log = getattr(self.object, 'locatorlog')
        log_entry = LocatorLogEntry(locator_log=locator_log)
        return LocatorLogEntryModelWrapper(log_entry)