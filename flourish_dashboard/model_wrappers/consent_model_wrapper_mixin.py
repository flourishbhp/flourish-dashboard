from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_base.utils import get_uuid

from edc_consent.site_consents import site_consents


class ConsentModelWrapperMixin:
    consent_model_wrapper_cls = None

    @property
    def screening_identifier(self):
        """ Returns screening identifier from the wrapped model object,
            or queries the latest consent instance for the screening_identifier.
        """
        if self.object:
            return self.object.screening_identifier
        else:
            return getattr(
                self.latest_consent_model_obj, 'screening_identifier', None)
        return None

    @property
    def consent_object(self):
        """Returns a consent configuration object from site_consents
        relative to the wrapper's "object" report_datetime.
        """
        consent_model_wrapper_cls = self.consent_model_wrapper_cls or self.__class__

        default_consent_group = django_apps.get_app_config(
            'edc_consent').default_consent_group
        consent_object = site_consents.get_consent_for_period(
            model=consent_model_wrapper_cls.model,
            report_datetime=self.screening_report_datetime,
            consent_group=default_consent_group,
            version=self.consent_version or None)
        return consent_object

    @property
    def subject_consent_cls(self):
        return django_apps.get_model('flourish_caregiver.subjectconsent')

    @property
    def consent_version_cls(self):
        return django_apps.get_model('flourish_caregiver.flourishconsentversion')

    @property
    def consent_version(self):
        version = None

        try:
            consent_version_obj = self.consent_version_cls.objects.get(
                screening_identifier=self.screening_identifier)
        except self.consent_version_cls.DoesNotExist:
            version = '1'
        else:
            version = consent_version_obj.version
        return version

    @property
    def child_consent_version(self):
        version = None
        try:
            consent_version_obj = self.consent_version_cls.objects.get(
                screening_identifier=self.screening_identifier)
        except self.consent_version_cls.DoesNotExist:
            pass
        else:
            version = consent_version_obj.child_version

        return version if version else self.consent_version

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
        model_obj = self.consent_model_obj or self.subject_consent_cls(
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
            version=self.consent_version
        )
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

    @property
    def child_consents(self):
        if self.consent_model_obj:
            return self.consent_model_obj.caregiverchildconsent_set.all()
        return []

    def set_initials(self, first_name=None, last_name=None):
        initials = ''
        if first_name and last_name:
            if (len(first_name.split(' ')) > 1):
                first = first_name.split(' ')[0]
                middle = first_name.split(' ')[1]
                initials = f'{first[:1]}{middle[:1]}{last_name[:1]}'
            else:
                initials = f'{first_name[:1]}{last_name[:1]}'
        return initials

    @property
    def children_eligibility(self):
        if self.object.caregiverchildconsent_set.all():
            eligible_children = self.object.caregiverchildconsent_set.filter(
                is_eligible=True)
            return False if not eligible_children else True
        return True

    @property
    def children_ineligible(self):
        if self.child_consents:
            return self.child_consents.filter(is_eligible=False)
        return []

    @property
    def latest_consent_model_obj(self):
        """Returns the latest consent instance by consent_datetime.
        """
        consents = self.subject_consent_cls.objects.filter(
            screening_identifier=self.object.screening_identifier)
        if consents:
            return consents.latest('consent_datetime')
