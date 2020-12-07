from django.conf import settings

from edc_model_wrapper.wrappers import ModelWrapper


class LocatorLogModelWrapper(ModelWrapper):

    model = 'flourish_caregiver.locatorlog'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_dataset_listboard_url')
    querystring_attrs = [
        'maternal_dataset', 'study_maternal_identifier']
    next_url_attrs = [
        'maternal_dataset', 'study_maternal_identifier']

    @property
    def study_maternal_identifier(self):
        return self.object.maternal_dataset.study_maternal_identifier

    @property
    def maternal_dataset(self):
        return self.object.maternal_dataset.id
