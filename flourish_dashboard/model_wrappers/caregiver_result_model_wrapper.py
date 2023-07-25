from django.apps import apps as django_apps
from edc_senaite_interface.model_wrappers import ResultModelWrapper


class CaregiverResultModelWrapper(ResultModelWrapper):

    model = 'flourish_caregiver.caregiverrequisitionresult'

    @property
    def result_model_wrapper_cls(self):
        return self

    @property
    def result_model_cls(self):
        return django_apps.get_model('flourish_caregiver.caregiverrequisitionresult')

    @property
    def dashboard_url(self):
        return 'flourish_dashboard:subject_dashboard_url'

    @property
    def results_objs(self):
        if self.object:
            return self.object.caregiverresultvalue_set.all()
        return {}
