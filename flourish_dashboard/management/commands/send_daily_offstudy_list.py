import django_rq
from rq import Retry
from django.apps import apps as django_apps
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from edc_base.utils import get_utcnow


from ...tasks import generate_offstudy_csv


class Command(BaseCommand):
    help = 'Send daily list of participants eligible for offstudy'

    def handle(self, *args, **kwargs):
        object_idx = list(
            self.child_consent_cls.objects.values_list(
                'subject_identifier', flat=True))
        filename_prefix = self.filename

        queue = django_rq.get_queue('exports')
        queue.enqueue(
            generate_offstudy_csv,
            object_idx,
            filename_prefix,
            self.receipients,
            self.child_consent_cls._meta.label_lower,
            retry=Retry(max=5),  # Retry failed tasks up to 5 times
        )

    @property
    def filename(self):
        return (
            f'offstudy_eligible_pids_{get_utcnow().date().strftime("%Y_%m_%d")}')

    @property
    def child_consent_cls(self):
        return django_apps.get_model(
            'flourish_child.childdummysubjectconsent')

    @property
    def receipients(self):
        return list(User.objects.filter(
            groups__name='Daily Email Updates').values_list(
                'email', flat=True))
