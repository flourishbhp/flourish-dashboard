from django.conf import settings
from edc_model_wrapper import ModelWrapper


class ChildConsentVersionModelWrapper(ModelWrapper):

    model = 'flourish_child.childconsentversion'
    visit_model_attr = 'child_visit'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'child_dashboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier', visit_model_attr]
