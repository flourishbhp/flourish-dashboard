from django.apps import apps as django_apps
from edc_base.utils import age, get_utcnow


class ChildDummyConsentModelWrapperMixin:

    @property
    def screening_identifier(self):
        subject_consent = self.subject_consent_cls.objects.filter(
            subject_identifier=self.caregiver_subject_identifier,)
        return subject_consent[0].screening_identifier

    @property
    def child_consent(self):
        """
        Returns a consent objects of the child from the caregiver consent
        """
        child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')

        childconsent = child_consent_cls.objects.filter(
            subject_identifier=self.object.subject_identifier).latest('consent_datetime')

        return childconsent

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
        else:
            childconsent = self.child_consent
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
        else:
            childconsent = self.child_consent
            birth_date = childconsent.child_dob
            if birth_date:
                years = age(birth_date, get_utcnow()).years
                return years

    @property
    def gender(self):
        if self.get_assent:
            return self.get_assent.gender
        else:
            childconsent = self.child_consent
            return childconsent.gender

    @property
    def child_dob(self):
        if self.get_assent:
            birth_date = self.get_assent.dob
            return birth_date
        else:
            childconsent = self.child_consent
            birth_date = childconsent.child_dob
            return birth_date

    @property
    def get_cohort(self):
        childconsent = self.child_consent
        if childconsent.cohort:
            cohort = childconsent.cohort.upper()
            return cohort.replace('_', ' ')

    @property
    def assent_date(self):
        if self.get_assent:
            return self.get_assent.consent_datetime.date()
        else:
            childconsent = self.child_consent
            consent_date = childconsent.consent_datetime.date()
            return consent_date

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
    def get_antenatal(self):
        getattr(self, 'maternal_delivery_obj')
