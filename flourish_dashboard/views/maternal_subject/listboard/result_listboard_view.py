from edc_senaite_interface.views import ListboardView

from ....model_wrappers import CaregiverResultModelWrapper
from ...view_mixin import ResultRefreshViewMixin


class ResultListboardView(ResultRefreshViewMixin, ListboardView):

    model = 'flourish_caregiver.caregiverrequisitionresult'
    model_wrapper_cls = CaregiverResultModelWrapper

    def get(self, request, *args, **kwargs):
        refresh_table = self.request.GET.get('refresh', False)
        if refresh_table:
            self.refresh_context_data(app_label='flourish_caregiver')
        return super().get(request, *args, **kwargs)
