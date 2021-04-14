from django.conf import settings

from edc_model_wrapper import ModelWrapper


class ChildOffstudyModelWrapper(ModelWrapper):

    model = 'flourish_prn.childoffstudy'
    next_url_name = settings.DASHBOARD_URL_NAMES.get('child_dashboard_url')
    next_url_attrs = ['subject_identifier']
    querystring_attrs = ['subject_identifier']
