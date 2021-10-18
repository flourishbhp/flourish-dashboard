from edc_visit_schedule.model_wrappers import RequisitionModelWrapper


class CaregiverRequisitionModelWrapper(RequisitionModelWrapper):

    visit_model_attr = 'maternal_visit'

    querystring_attrs = [visit_model_attr, 'panel']

    @property
    def maternal_visit(self):
        return str(getattr(self.object, self.visit_model_attr).id)
