from django.conf import settings

from edc_model_wrapper import ModelWrapper


class YoungAdultLocatorModelWrapper(ModelWrapper):
    model = 'flourish_child.youngadultlocator'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'child_dashboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier']
