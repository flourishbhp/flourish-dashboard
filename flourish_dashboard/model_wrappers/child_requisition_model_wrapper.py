from django.conf import settings
from edc_visit_schedule.model_wrappers import RequisitionModelWrapper

class ChildRequisitionModelWrapper(RequisitionModelWrapper):

    visit_model_attr = 'child_visit'

    querystring_attrs = [visit_model_attr, 'panel']

    model = 'flourish_child.childrequisition'

    next_url_name = settings.DASHBOARD_URL_NAMES.get('child_dashboard_url')
    next_url_attrs = ['appointment', 'subject_identifier']

    @property
    def child_visit(self):
        return str(getattr(self.object, self.visit_model_attr).id)
