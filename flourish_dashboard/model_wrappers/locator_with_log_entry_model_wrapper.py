from django.conf import settings
from edc_model_wrapper.wrappers import ModelWithLogWrapper

from .locator_log_entry_model_wrapper import LocatorLogEntryModelWrapper


class LocatorWithLogEntryModelWrapper(ModelWithLogWrapper):

    model = 'flourish_caregiver.maternaldataset'
    
    related_lookup = 'locator_log'
    log_model_name = 'locator_log'
    log_entry_model_name = 'locator_log_entry'
    
    log_entry_model_wrapper_cls = LocatorLogEntryModelWrapper
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_dataset_listboard_url')
    querystring_attrs = [
        'screening_identifier', 'subject_identifier',
        'study_maternal_identifier', 'study_child_identifier']
    next_url_attrs = [
        'screening_identifier', 'subject_identifier',
        'study_maternal_identifier', 'study_child_identifier']

    @property
    def maternal_dataset(self):
        return self.object