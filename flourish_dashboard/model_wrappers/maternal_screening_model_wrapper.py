from django.conf import settings
from edc_model_wrapper import ModelWrapper


class MaternalScreeningModelWrapper(ModelWrapper):

    model = 'flourish_maternal.subjectscreening'
    querystring_attrs = ['screening_identifier']
    next_url_attrs = ['screening_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'maternal_screening_listboard_url')
