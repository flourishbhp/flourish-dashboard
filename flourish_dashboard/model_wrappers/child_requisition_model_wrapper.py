from edc_visit_schedule.model_wrappers import RequisitionModelWrapper


class ChildRequisitionModelWrapper(RequisitionModelWrapper):

    visit_model_attr = 'child_visit'

    querystring_attrs = [visit_model_attr, 'panel']

    model = 'flourish_child.childrequisition'

    @property
    def child_visit(self):
        return str(getattr(self.object, self.visit_model_attr).id)
