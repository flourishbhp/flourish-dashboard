from django.contrib.auth.decorators import login_required
from django.urls.base import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ...forms import LocatorLogReportForm


class LocatorLogReportView(
        EdcBaseViewMixin, NavbarViewMixin,
        TemplateView, FormView):

    form_class = LocatorLogReportForm
    template_name = 'flourish_dashboard/maternal_dataset/locator_report.html'
    navbar_name = 'flourish_dashboard'
    navbar_selected_item = 'maternal_dataset'

    def get_success_url(self):
        return reverse('flourish_dashboard:locator_report_url')

    def form_valid(self, form):
        if form.is_valid():
            pass
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            locator_logs=[],
            total_locators=2,
            not_found=3)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
