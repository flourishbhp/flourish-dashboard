from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_base.utils import get_uuid

from edc_consent.site_consents import site_consents


class ConsentModelWrapperMixin:

    consent_model_wrapper_cls = None

    @property
    def consent_object(self):
        """Returns a consent configuration object from site_consents
        relative to the wrapper's "object" report_datetime.
        """
        default_consent_group = django_apps.get_app_config(
            'edc_consent').default_consent_group
        consent_object = site_consents.get_consent_for_period(
            model=self.consent_model_wrapper_cls.model,
            report_datetime=self.screening_report_datetime,
            consent_group=default_consent_group,
            version=self.consent_version or None)
        return consent_object

    @property
    def subject_consent_cls(self):
        return django_apps.get_model('flourish_caregiver.subjectconsent')

    @property
    def consent_version(self):
        return '1'

    @property
    def consent_model_obj(self):
        """Returns a consent model instance or None.
        """
        try:
            return self.subject_consent_cls.objects.get(**self.consent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def consent(self):
        """Returns a wrapped saved or unsaved consent.
        """
        model_obj = self.consent_model_obj or self.consent_object.model_cls(
            **self.create_consent_options)
        return self.consent_model_wrapper_cls(model_obj=model_obj)

    @property
    def create_consent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted consent model instance.
        """
        options = dict(
            screening_identifier=self.screening_identifier,
            consent_identifier=get_uuid(),
            version=self.consent_version)
        if getattr(self, 'locator_model_obj'):
            first_name = self.locator_model_obj.first_name.upper()
            last_name = self.locator_model_obj.last_name.upper()
            initials = ''
            if (len(first_name.split(' ')) > 1):
                first = first_name.split(' ')[0]
                middle = first_name.split(' ')[1]
                initials = f'{first[:1]}{middle[:1]}{last_name[:1]}'
            else:
                initials = f'{first_name[:1]}{last_name[:1]}'
            options.update(
                {'first_name': first_name,
                 'last_name': last_name,
                 'initials': initials,
                 'child_dob': self.delivdt})
        return options

    @property
    def consent_options(self):
        """Returns a dictionary of options to get an existing
        consent model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier,
            version=self.consent_version)
        return options
