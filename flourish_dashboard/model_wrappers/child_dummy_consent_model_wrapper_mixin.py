from django.apps import apps as django_apps
from edc_base.utils import age, get_utcnow
from django.core.exceptions import ValidationError



class ChildDummyConsentModelWrapperMixin:

    cohort_model = 'flourish_caregiver.cohort'
    
    @property
    def cohort_model_cls(self):
        return django_apps.get_model(self.cohort_model)

    @property
    def registered_subject_cls(self):
        return django_apps.get_model('edc_registration.registeredsubject')

    @property
    def screening_identifier(self):
        subject_consent = self.subject_consent_cls.objects.filter(
            subject_identifier=self.caregiver_subject_identifier, ).first()
        return getattr(subject_consent, 'screening_identifier', None)

    @property
    def child_consent(self):
        """
        Returns a consent objects of the child from the caregiver consent
        """
        child_consent_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')

        try:
            childconsent = child_consent_cls.objects.filter(
                subject_identifier=self.object.subject_identifier).latest('consent_datetime')
        except child_consent_cls.DoesNotExist:
            return None
        return childconsent

    @property
    def caregiver_subject_identifier(self):
        try:
            registered_subject = self.registered_subject_cls.objects.get(
                subject_identifier=self.object.subject_identifier)
        except self.registered_subject_cls.DoesNotExist:
            return None
        else:
            return getattr(registered_subject, 'relative_identifier', None)

    @property
    def child_name_initial(self):
        childconsent = self.child_consent
        if self.get_assent:
            name = self.get_assent.first_name
            initials = self.get_assent.initials
            return f'{name} {initials}'
        elif childconsent:
            first_name = childconsent.first_name
            last_name = childconsent.last_name
            if first_name and last_name:
                return f'{first_name} {first_name[0]}{last_name[0]}'
        return None

    @property
    def child_age(self):
        childconsent = self.child_consent
        if self.get_assent:
            birth_date = self.get_assent.dob
            years = age(birth_date, get_utcnow()).years
            return years
        elif childconsent:
            birth_date = childconsent.child_dob
            if birth_date:
                years = age(birth_date, get_utcnow()).years
                return years

    @property
    def gender(self):
        childconsent = self.child_consent
        if self.get_assent:
            return self.get_assent.gender
        elif childconsent:
            return childconsent.gender

    @property
    def child_dob(self):
        childconsent = self.child_consent
        if self.get_assent:
            birth_date = self.get_assent.dob
            return birth_date
        elif childconsent:
            birth_date = childconsent.child_dob
            return birth_date

    @property
    def get_cohort(self):
        childconsent = self.child_consent
        if childconsent.cohort:
            cohort = childconsent.cohort.upper()
            return cohort.replace('_', ' ')

    @property
    def enrol_cohort(self):
        """Returns an enrollment cohort.
        """
        try:
            cohort = self.cohort_model_cls.objects.get(
                subject_identifier=self.object.subject_identifier,
                enrollment_cohort=True, )
        except self.cohort_model_cls.DoesNotExist:
            raise ValidationError(
                f"Enrollment Cohort is missing, {self.object.subject_identifier}")
        else:
            return cohort.name

    @property
    def current_cohort(self):
        """Returns the current cohort.
        """
        cohort = self.cohort_model_cls.objects.filter(
            subject_identifier=self.object.subject_identifier)
        if cohort.exists():
            cohort = cohort.latest('assign_datetime')
            return cohort.name
        return None

    @property
    def assent_date(self):
        childconsent = self.child_consent
        if self.get_assent:
            return self.get_assent.consent_datetime.date()
        elif childconsent:
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
        return getattr(self, 'assent_model_obj', None)

    @property
    def get_antenatal(self):
        getattr(self, 'maternal_delivery_obj', None)
