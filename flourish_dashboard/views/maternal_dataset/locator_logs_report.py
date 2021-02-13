from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin
from flourish_caregiver.models import CaregiverLocator, LocatorLogEntry

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

    @property
    def total_locators(self):
        """Returns totall number of locators.
        """
        return CaregiverLocator.objects.all().count()

    @property
    def locator_user_stats(self):
        """Returns stats of logs of all users who captured locators.
        """
        log_stats = []
        users = User.objects.filter(groups__name='locator users')
        for user in users:
            found = LocatorLogEntry.objects.filter(
                user_created=user.username,
                log_status='exist').count()
            missing = LocatorLogEntry.objects.filter(
                user_created=user.username,
                log_status='not_found').count()
            captured = CaregiverLocator.objects.filter(user_created=user.username).count()
            log_stats.append([user.username, found, missing, captured])
        return log_stats

    @property
    def locators_not_found(self):
        """Returns total locators not found.
        """
        return LocatorLogEntry.objects.filter(log_status='not_found').count()

    def locator_log_entries(self, user_created=None, start_date=None, end_date=None):
        if user_created and not start_date and not end_date:
            return LocatorLogEntry.objects.filter(user_created=user_created)
        elif user_created and start_date and end_date:
            return LocatorLogEntry.objects.filter(
                date_created__range=[start_date, end_date],
                user_created=user_created)
        elif start_date and end_date and not user_created:
            LocatorLogEntry.objects.filter(
                date_created__range=[start_date, end_date])
            return LocatorLogEntry.objects.filter(
                date_created__range=[start_date, end_date])
        return LocatorLogEntry.objects.all()

    def get(self, request, *args, **kwargs):
        form = LocatorLogReportForm(request.GET or None)
        user_created = None
        start_date = None
        end_date = None
        if form.is_valid():
            user_created = form.cleaned_data['username']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
        self.log_entries = self.locator_log_entries(
            user_created=user_created,
            start_date=start_date,
            end_date=end_date)
        return super(LocatorLogReportView, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            locator_logs=[],
            total_locators=self.total_locators,
            not_found=self.locators_not_found,
            locator_log_entries=self.log_entries,
            locator_user_stats=self.locator_user_stats)
        return context

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
