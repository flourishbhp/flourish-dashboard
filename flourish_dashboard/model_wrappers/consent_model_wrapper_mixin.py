from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_base.utils import get_uuid

from edc_consent.site_consents import site_consents
from edc_constants.constants import FEMALE


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
        if getattr(self, 'bhp_prior_screening_model_obj'):
            bhp_prior_screening = self.bhp_prior_screening_model_obj
            flourish_participation = bhp_prior_screening.flourish_participation
            if flourish_participation == 'interested' and getattr(self, 'locator_model_obj'):
                first_name = self.locator_model_obj.first_name
                last_name = self.locator_model_obj.last_name
                initials = self.set_initials(first_name, last_name)
                options.update(
                    {'first_name': first_name.upper(),
                     'last_name': last_name.upper(),
                     'initials': initials,
                     'gender': FEMALE})
        return options

    @property
    def consent_options(self):
        """Returns a dictionary of options to get an existing
        consent model instance.
        """
        options = dict(
            screening_identifier=self.screening_identifier,
            version=self.consent_version)
        return options

    @property
    def show_dashboard(self):
        show_dashboard = False
        subject_consent = self.consent_model_obj
        if subject_consent:
            child_consents = subject_consent.caregiverchildconsent_set.all()
            for child_consent in child_consents:
                child_age = child_consent.child_age_at_enrollment
                if child_consent.is_eligible and child_age < 7:
                    show_dashboard = True
                    break
                elif child_consent.is_eligible and child_age > 7:
                    assent_obj = getattr(self, 'child_assent_obj', None)
                    if assent_obj:
                        child_assent = assent_obj(
                            subject_identifier=child_consent.subject_identifier,)
                        show_dashboard = True if child_assent else False
                        break
        return show_dashboard

    def set_initials(self, first_name, last_name):
        initials = ''
        if (len(first_name.split(' ')) > 1):
            first = first_name.split(' ')[0]
            middle = first_name.split(' ')[1]
            initials = f'{first[:1]}{middle[:1]}{last_name[:1]}'
        else:
            initials = f'{first_name[:1]}{last_name[:1]}'
        return initials
