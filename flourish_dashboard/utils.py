from django.apps import apps as django_apps
from edc_base.utils import age, get_utcnow


class FlourishDashboardUtils:

    def child_age(self, infant_dob):
        years = None
        if infant_dob:
            birth_date = infant_dob
            child_age = age(birth_date, get_utcnow())
            years = round(child_age.years + (child_age.months / 12), 2)
        return years if years else 0

    def is_delivery_window(self, subject_identifier):

        maternal_delivery_cls = django_apps.get_model(
            'flourish_caregiver.maternaldelivery')

        preg_screen_cls = django_apps.get_model(
            'flourish_caregiver.screeningpregwomen')

        try:
            screen_obj = preg_screen_cls.objects.get(
                subject_identifier=subject_identifier)
        except preg_screen_cls.DoesNotExist:
            return False
        else:
            is_delivery_window = []
            for obj in screen_obj.screeningpregwomeninline_set.all():
                try:
                    maternal_delivery_obj = maternal_delivery_cls.objects.get(
                        subject_identifier=subject_identifier,
                        child_subject_identifier=obj.child_subject_identifier
                    )
                except maternal_delivery_cls.DoesNotExist:
                    is_delivery_window.append(True)
                else:
                    is_delivery_window.append(
                        (get_utcnow().date() -
                         maternal_delivery_obj.delivery_datetime.date()).days <= 3)
            return any(is_delivery_window)

    def requires_child_version(self, subject_identifier, screening_identifier):

        consent_version_cls = django_apps.get_model(
            'flourish_caregiver.flourishconsentversion')
        try:
            consent_version_obj = consent_version_cls.objects.get(
                screening_identifier=screening_identifier)
        except consent_version_cls.DoesNotExist:
            return False
        else:
            return (self.is_delivery_window(subject_identifier)
                    and not consent_version_obj.child_version)


flourish_dashboard_utils = FlourishDashboardUtils()
