from edc_senaite_interface.views import ListboardView

from ....model_wrappers import ChildResultModelWrapper
from ...view_mixin import ResultRefreshViewMixin


class ResultListboardView(ResultRefreshViewMixin, ListboardView):

    listboard_url = 'child_result_listboard_url'

    model = 'flourish_child.childrequisitionresult'
    model_wrapper_cls = ChildResultModelWrapper

    def get(self, request, *args, **kwargs):
        refresh_table = self.request.GET.get('refresh', False)
        if refresh_table:
            self.refresh_context_data(app_label='flourish_child')
        return super().get(request, *args, **kwargs)
