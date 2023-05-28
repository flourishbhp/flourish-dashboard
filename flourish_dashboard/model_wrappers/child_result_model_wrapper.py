from django.apps import apps as django_apps
from edc_senaite_interface.model_wrappers import ResultModelWrapper


class ChildResultModelWrapper(ResultModelWrapper):

    model = 'flourish_child.childrequisitionresult'

    @property
    def result_model_wrapper_cls(self):
        return self

    @property
    def result_model_cls(self):
        return django_apps.get_model('flourish_child.childrequisitionresult')

    @property
    def dashboard_url(self):
        return 'flourish_dashboard:child_dashboard_url'

    @property
    def results_objs(self):
        if self.object:
            return self.object.childresultvalue_set.all()
