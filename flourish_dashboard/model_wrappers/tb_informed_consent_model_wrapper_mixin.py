from datetime import datetime

import pytz
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_aware
from edc_consent.site_consents import site_consents

from .tb_informed_consent_model_wrapper import TbInformedConsentModelWrapper


class TbInformedConsentModelWrapperMixin:
    consent_model_wrapper_cls = TbInformedConsentModelWrapper

    @property
    def tb_consent_model_obj(self):
        """Returns a tb consent model instance or None.
        """
        try:
            return self.tb_consent_cls.objects.get(
                **self.tb_informed_consent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def tb_consent(self):
        """"Returns a wrapped saved or unsaved tb consent
        """
        model_obj = self.tb_consent_model_obj or self.tb_consent_cls(
            **self.create_tb_informed_consent_options)
        return TbInformedConsentModelWrapper(model_obj=model_obj)

    @property
    def tb_consent_cls(self):
        return django_apps.get_model('flourish_caregiver.tbinformedconsent')

    @property
    def create_tb_informed_consent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted tb consent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            version=self.tb_consent_version,
            first_name=self.object.first_name,
            last_name=self.object.last_name,
            initials=self.object.initials,
            gender=self.object.gender,
            dob=self.object.dob,
            identity=self.object.identity,
            identity_type=self.object.identity_type,
            language=self.object.language,
            is_literate=self.object.is_literate,
            witness_name=self.object.witness_name,
            is_dob_estimated=self.object.is_dob_estimated,
            confirm_identity=self.object.confirm_identity,
            )
        return options

    @property
    def tb_informed_consent_options(self):
        """Returns a dictionary of options to get an existing
         tb consent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            version=self.tb_consent_version,
            )
        return options

    @property
    def tb_consent_version(self):
        current_datetime = datetime.now()
        tz = pytz.timezone('Africa/Gaborone')
        consent_datetime = make_aware(current_datetime, tz, True)
        consent = site_consents.get_consent_for_period(
            self.consent_model_wrapper_cls.model,
            report_datetime=consent_datetime)
        return consent.version
