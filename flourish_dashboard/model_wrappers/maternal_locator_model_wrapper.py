from django.conf import settings

from edc_model_wrapper import ModelWrapper


class MaternalLocatorModelWrapper(ModelWrapper):

    model = 'flourish_maternal.maternallocator'
    next_url_name = settings.DASHBOARD_URL_NAMES.get('subject_dashboard_url')
    next_url_attrs = ['subject_identifier']
