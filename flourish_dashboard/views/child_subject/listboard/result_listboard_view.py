from django.urls import reverse
from edc_senaite_interface.views import ListboardView

from ....model_wrappers import ChildResultModelWrapper
from ...view_mixin import ResultRefreshViewMixin


class ResultListboardView(ResultRefreshViewMixin, ListboardView):

    listboard_url = 'child_result_listboard_url'

    model = 'flourish_child.childrequisitionresult'
    model_wrapper_cls = ChildResultModelWrapper

    def get(self, request, *args, **kwargs):
        refresh_table = kwargs.get('refresh', False)
        if refresh_table:
            self.refresh_context_data(app_label='flourish_child')
        return super().get(request, *args, **kwargs)

    def dashboard_link(self, participant_id=None, dashboard_url=''):
        dashboard_url = 'flourish_dashboard:child_dashboard_url'
        url_link = reverse(dashboard_url, kwargs={'subject_identifier': participant_id})
        url_link = f'<a href="{url_link}"> {participant_id} </a>'
        return url_link
