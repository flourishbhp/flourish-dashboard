import django_rq
import pytz
from rq import Retry
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib import messages
from django.views.generic.base import ContextMixin
from django.shortcuts import redirect

from edc_base.utils import get_utcnow

from flourish_dashboard.tasks import generate_offstudy_csv


tz = pytz.timezone('Africa/Gaborone')


class OffStudyExportViewMixin(ContextMixin):

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        export = self.request.GET.get('export', '')
        if export:
            user_email = request.user.email

            if not user_email:
                messages.error(request, 'No email address found for user.')
                return redirect(request.path)
            try:
                validate_email(user_email)
            except ValidationError:
                messages.error(request, 'The email address for user is not valid.')
                return redirect(request.path)

            object_idx = list(
                self.object_list.values_list('subject_identifier', flat=True))
            filename_prefix = self.filename

            queue = django_rq.get_queue('exports')
            queue.enqueue(
                generate_offstudy_csv,
                object_idx,
                filename_prefix,
                [user_email, ],
                self.model,
                retry=Retry(max=5),  # Retry failed tasks up to 5 times
            )

            messages.success(
                request,
                'Your request is being processed. The file will be '
                'sent to your email once complete.')
            return redirect(request.path)
        return response

    @property
    def filename(self):
        file_name = (
            f'offstudy_eligible_pids_{get_utcnow().date().strftime("%Y_%m_%d")}')

        download_path = f'{file_name}'
        return download_path
