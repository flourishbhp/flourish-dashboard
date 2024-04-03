from datetime import datetime

from django.apps import apps as django_apps
from edc_base.utils import age, get_utcnow

caregiver_config = django_apps.get_app_config('flourish_caregiver')


class ModelUtils:
    def get_model_object(self, model_name, **kwargs):
        model_cls = django_apps.get_model(model_name)
        try:
            return model_cls.objects.get(**kwargs)
        except model_cls.DoesNotExist:
            return None


class ChildUtils:
    @staticmethod
    def calculate_age(dob):
        years = 0
        if dob:
            dob = datetime.strptime(dob, "%Y-%m-%d")
            child_age = age(dob, get_utcnow())
            years = round(child_age.years + (child_age.months / 12), 2)
        return years

    @staticmethod
    def is_minor(dob):
        return ChildUtils.calculate_age(dob) < 18


class FlourishDashboardUtils(ModelUtils, ChildUtils):

    def is_delivery_window(self, subject_identifier):
        preg_screen_cls = 'flourish_caregiver.screeningpregwomen'
        maternal_delivery_cls = 'flourish_caregiver.maternaldelivery'

        screen_obj = self.get_model_object(preg_screen_cls,
                                           subject_identifier=subject_identifier)

        if not screen_obj:
            return False

        is_delivery_window = []
        for obj in screen_obj.screeningpregwomeninline_set.all():
            maternal_delivery_obj = self.get_model_object(
                maternal_delivery_cls,
                subject_identifier=subject_identifier,
                child_subject_identifier=obj.child_subject_identifier
            )

            if not maternal_delivery_obj:
                is_delivery_window.append(True)
            else:
                is_delivery_window.append(
                    (get_utcnow().date() -
                     maternal_delivery_obj.delivery_datetime.date()).days <= 3)

        return any(is_delivery_window)

    def requires_child_version(self, subject_identifier, screening_identifier):
        consent_version_cls = 'flourish_caregiver.flourishconsentversion'

        consent_version_obj = self.get_model_object(
            consent_version_cls,
            screening_identifier=screening_identifier)

        if not consent_version_obj:
            return False

        return self.is_delivery_window(
            subject_identifier) and not consent_version_obj.child_version

    def screening_object_by_child_pid(self, screening_identifier,
                                      child_subject_identifier):
        screening_model_cls = 'flourish_caregiver.screeningpregwomen'

        screening_obj = self.get_model_object(
            screening_model_cls,
            screening_identifier=screening_identifier)

        if not screening_obj:
            return None

        return screening_obj.screeningpregwomeninline_set.filter(
            child_subject_identifier=child_subject_identifier)

    def consent_version_obj(self, screening_identifier=None):
        consent_version_cls = django_apps.get_model(
            'flourish_caregiver.flourishconsentversion')
        try:
            consent_version_obj = consent_version_cls.objects.get(
                screening_identifier=screening_identifier)
        except consent_version_cls.DoesNotExist:
            return None
        else:
            return consent_version_obj

    def is_latest_consent_version(self, screening_identifier=None):
        consent_version_obj = self.consent_version_obj(screening_identifier)
        return str(consent_version_obj.child_version) == str(
            caregiver_config.consent_version)

    def get_minor_assents(self, assents):
        return [child_assent for child_assent in assents if
                child_assent.dob and self.is_minor(child_assent.dob)]

    def consent_version_obj(self, screening_identifier=None):
        consent_version_cls = django_apps.get_model(
            'flourish_caregiver.flourishconsentversion')
        try:
            consent_version_obj = consent_version_cls.objects.get(
                screening_identifier=screening_identifier)
        except consent_version_cls.DoesNotExist:
            return None
        else:
            return consent_version_obj

    def is_latest_consent_version(self, screening_identifier=None):
        consent_version_obj = self.consent_version_obj(screening_identifier)
        return str(consent_version_obj.child_version) == str(
            caregiver_config.consent_version)


flourish_dashboard_utils = FlourishDashboardUtils()
