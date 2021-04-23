from django.conf import settings
from edc_model_wrapper import ModelWrapper


class BHPPriorScreeningModelWrapper(ModelWrapper):

    model = 'flourish_caregiver.screeningpriorbhpparticipants'
    querystring_attrs = ['screening_identifier', 'study_maternal_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'maternal_dataset_listboard_url')
    next_url_attrs = ['study_maternal_identifier', ]

    @property
    def study_maternal_identifier(self):
        return self.object.study_maternal_identifier
