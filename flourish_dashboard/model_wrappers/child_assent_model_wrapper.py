from django.conf import settings

from edc_model_wrapper import ModelWrapper


class ChildAssentModelWrapper(ModelWrapper):

    model = 'flourish_child.childassent'
    querystring_attrs = ['screening_identifier', 'subject_identifier']
    next_url_attrs = ['screening_identifier', 'subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'subject_listboard_url')
