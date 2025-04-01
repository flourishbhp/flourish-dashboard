from django.conf import settings

from edc_model_wrapper import ModelWrapper


class ChildContinuedConsentModelWrapper(ModelWrapper):

    model = 'flourish_child.childcontinuedconsent'
    querystring_attrs = ['subject_identifier', 'version']
    next_url_attrs = ['subject_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'child_dashboard_url')
