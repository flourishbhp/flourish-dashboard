from django.conf import settings

from edc_model_wrapper import ModelWrapper


class MaternalLocatorModelWrapper(ModelWrapper):

    model = 'flourish_maternal.maternallocator'
    querystring_attrs = ['subject_identifier']
    next_url_attrs = ['screening_identifier', 'subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_dataset_listboard_url')
    