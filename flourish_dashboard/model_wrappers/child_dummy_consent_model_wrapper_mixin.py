from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from edc_base.utils import age, get_utcnow


class ChildDummyConsentModelWrapperMixin:

    @property
    def screening_identifier(self):
        subject_consent = self.subject_consent_cls.objects.get(
            subject_identifier=self.caregiver_subject_identifier)
        return subject_consent.screening_identifier

    @property
    def assent_options(self):
        """Returns a dictionary of options to get an existing
         child assent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            version=self.version)
        return options

    @property
    def consent_options(self):
        """Returns a dictionary of options to get an existing
        consent model instance.
        """
        options = dict(
            subject_identifier=self.caregiver_subject_identifier,
            version=self.consent_version)
        return options

    @property
    def caregiver_subject_identifier(self):
        subject_identifier = self.object.subject_identifier.split('-')
        subject_identifier.pop()
        caregiver_subject_identifier = '-'.join(subject_identifier)
        return caregiver_subject_identifier

    @property
    def child_name_initial(self):
        if self.get_assent:
            name = self.get_assent.first_name
            initials = self.get_assent.initials
            return f'{name} {initials}'
        elif self.get_consent:
            childconsent = self.get_consent.caregiverchildconsent_set.get(
                subject_identifier=self.object.subject_identifier)
            first_name = childconsent.first_name
            last_name = childconsent.last_name
            if first_name and last_name:
                return f'{first_name} {first_name[0]}{last_name[0]}'
        return None

    @property
    def child_age(self):
        if self.get_assent:
            birth_date = self.get_assent.dob
            years = age(birth_date, get_utcnow()).years
            return years
        elif self.get_consent:
            childconsent = self.get_consent.caregiverchildconsent_set.get(
                subject_identifier=self.object.subject_identifier)
            birth_date = childconsent.child_dob
            if birth_date:
                years = age(birth_date, get_utcnow()).years
                return years
        elif self.get_antenatal:
            birth_date = self.get_antenatal.delivery_datetime.date()
            years = age(birth_date, get_utcnow()).months
            return years
        return 0

    @property
    def gender(self):
        if self.get_assent:
            return self.get_assent.gender
        elif self.get_consent:
            childconsent = self.get_consent.caregiverchildconsent_set.get(
                subject_identifier=self.object.subject_identifier)
            return childconsent.gender

    @property
    def child_dob(self):
        if self.get_assent:
            birth_date = self.get_assent.dob
            return birth_date
        elif self.get_consent:
            childconsent = self.get_consent.caregiverchildconsent_set.get(
                subject_identifier=self.object.subject_identifier)
            birth_date = childconsent.child_dob
            return birth_date
        elif self.get_antenatal:
            birth_date = self.get_antenatal.delivery_datetime.date()
            return birth_date
        return 0

    @property
    def get_cohort(self):
        if self.object.cohort:
            cohort = self.object.cohort.upper()
            return cohort.replace('_', ' ')

    @property
    def assent_date(self):
        if self.get_assent:
            return self.get_assent.consent_datetime.date()
        elif self.get_consent:
            childconsent = self.get_consent.caregiverchildconsent_set.get(
                subject_identifier=self.object.subject_identifier)

            consent_date = childconsent.consent_datetime.date()
            return consent_date
        return 'N/A'

    @property
    def maternal_delivery_obj(self):
        maternal_delivery_cls = django_apps.get_model(
            'flourish_caregiver.maternaldelivery')
        try:
            maternal_delivery_obj = maternal_delivery_cls.objects.get(
                subject_identifier=self.caregiver_subject_identifier)
        except maternal_delivery_cls.DoesNotExist:
            return None
        else:
            return maternal_delivery_obj

    @property
    def get_assent(self):
        return getattr(self, 'assent_model_obj')

    @property
    def get_consent(self):
        return getattr(self, 'consent_model_obj')

    @property
    def get_antenatal(self):
        getattr(self, 'maternal_delivery_obj')
