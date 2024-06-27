from django.apps import apps as django_apps
from django.db.models import Q
from django.contrib import messages
from django.core import management
from django.core.management.base import CommandError


class ResultRefreshViewMixin:

    def refresh_context_data(self, app_label=''):
        """ Refresh requisition result information, exclude requisition that
            are not yet connected to the LIMS.
        """
        result_model_cls = django_apps.get_model(self.model)
        # sample_ids = result_model_cls.objects.values_list('sample_id', flat=True)

        requisition_model = result_model_cls.requisition_model
        requisition_model_cls = django_apps.get_model(requisition_model)

        pending_samples = requisition_model_cls.objects.exclude(
            sample_id='').values_list('sample_id', flat=True)

        pending_ids = ', '.join(pending_samples)
        try:
            management.call_command(
                'pull_results', sample_ids=pending_ids, app_label=app_label)
        except (CommandError, Exception):
            messages.add_message(
                self.request, messages.INFO,
                'Failed to pull all results. Please contact the administrator for assistance.')
