from django.conf import settings
from edc_model_wrapper import ModelWrapper


class ChildDatasetModelWrapper(ModelWrapper):

    model = 'flourish_child.childdataset'
    querystring_attrs = [
        'subject_identifier', 'study_maternal_identifier',
        'study_child_identifier']
    next_url_attrs = ['study_maternal_identifier', 'study_child_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'child_dashboard_url')
