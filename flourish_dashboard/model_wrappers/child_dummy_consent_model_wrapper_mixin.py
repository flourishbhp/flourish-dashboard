from django.apps import apps as django_apps

from dateutil.relativedelta import relativedelta
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
        import pdb; pdb.set_trace()
        subject_identifier = self.object.subject_identifier.split('-')
        subject_identifier.pop()
        caregiver_subject_identifier = '-'.join(subject_identifier)
        return caregiver_subject_identifier

    @property
    def child_name_initial(self):
        if getattr(self, 'assent_model_obj'):
            name = self.assent_model_obj.first_name
            initials = self.assent_model_obj.initials
            return f'{name} {initials}'
        elif getattr(self, 'consent_model_obj'):
            caregiverchildconsent_objs = self.consent_model_obj.caregiverchildconsent_set.all()
            for caregiverchildconsent_obj in caregiverchildconsent_objs:
                first_name = caregiverchildconsent_obj.first_name
                last_name = caregiverchildconsent_obj.first_name
                return f'{first_name} {first_name[0]}{last_name[0]}'
        return None

    @property
    def child_age(self):
        if getattr(self, 'assent_model_obj'):
            birth_date = self.assent_model_obj.dob
            years = age(birth_date, get_utcnow()).years
            return years
        elif getattr(self, 'consent_model_obj'):
            caregiverchildconsent_objs = self.consent_model_obj.caregiverchildconsent_set.all()
            for caregiverchildconsent_obj in caregiverchildconsent_objs:
                birth_date = caregiverchildconsent_obj.child_dob
                years = age(birth_date, get_utcnow()).years
                return years
        elif getattr(self, 'maternal_delivery_obj'):
            birth_date = self.maternal_delivery_obj.delivery_datetime.date()
            years = age(birth_date, get_utcnow()).months
            return years
        return 0

    @property
    def child_dob(self):
        if getattr(self, 'assent_model_obj'):
            birth_date = self.assent_model_obj.dob
            return birth_date
        elif getattr(self, 'consent_model_obj'):
            caregiverchildconsent_objs = self.consent_model_obj.caregiverchildconsent_set.all()
            for caregiverchildconsent_obj in caregiverchildconsent_objs:
                birth_date = caregiverchildconsent_obj.child_dob
                return birth_date
        elif getattr(self, 'maternal_delivery_obj'):
            birth_date = self.maternal_delivery_obj.delivery_datetime.date()
            return birth_date
        return 0

    @property
    def get_cohort(self):
        cohort = self.object.cohort.upper()
        return cohort.replace('_', ' ')

    @property
    def assent_date(self):
        if getattr(self, 'assent_model_obj'):
            return self.assent_model_obj.consent_datetime.date()
        elif getattr(self, 'consent_model_obj'):
            caregiverchildconsent_objs = self.consent_model_obj.caregiverchildconsent_set.all()
            for caregiverchildconsent_obj in caregiverchildconsent_objs:
                consent_date = caregiverchildconsent_obj.consent_datetime.date()
                return consent_date
        return 'N/A'

    @property
    def maternal_delivery_obj(self):
        maternal_delivery_cls = django_apps.get_model(
            'flourish_caregiver.maternaldelivery')
        maternal_delivery_obj = maternal_delivery_cls.objects.get(
            subject_identifier=self.caregiver_subject_identifier)
        return maternal_delivery_obj
