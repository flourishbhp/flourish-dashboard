from django.conf import settings

from edc_model_wrapper.wrappers import ModelWrapper


class LocatorLogEntryModelWrapper(ModelWrapper):

    model = 'flourish_caregiver.locatorlogentry'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_dataset_listboard_url')
    querystring_attrs = ['locator_log']
    next_url_attrs = ['locator_log']

    @property
    def study_maternal_identifier(self):
        return self.object.locator_log.study_maternal_identifier

    @property
    def locator_log(self):
        return self.object.locator_log.id