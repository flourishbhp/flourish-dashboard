from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from edc_base.utils import get_utcnow
from flourish_child.models import ChildAssent

from .child_assent_model_wrapper import ChildAssentModelWrapper


class ChildAssentModelWrapperMixin:
    assent_model_wrapper_cls = ChildAssentModelWrapper

    @property
    def assent_model_cls(self):
        return django_apps.get_model('flourish_child.childassent')

    @property
    def consent_version_cls(self):
        return django_apps.get_model('flourish_caregiver.flourishconsentversion')

    @property
    def subject_consent_cls(self):
        return django_apps.get_model('flourish_caregiver.subjectconsent')

    @property
    def assent_model_obj(self):
        """Returns a child assent model instance or None.
        """
        try:
            return self.assent_model_cls.objects.filter(
                **self.assent_options).latest('consent_datetime')
        except ObjectDoesNotExist:
            return None

    @property
    def child_assent(self):
        """"Returns a wrapped saved or unsaved child assent
        """
        if self.child_age >= 7:
            model_obj = self.assent_model_obj or self.assent_model_cls(
                **self.create_child_assent_options(self.caregiverchildconsent_obj))

            return ChildAssentModelWrapper(model_obj=model_obj)

    @property
    def current_version(self):
        """
        Get the version of the current passed consent
        """
        if self.consent_model_obj:
            return self.consent_model_obj.version

    @property
    def create_assent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted child assent model instance.
        """

        options = dict(
            screening_identifier=self.screening_identifier)
        return options

    @property
    def assent_options(self):
        """Returns a dictionary of options to get an existing
         child assent model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier,
            identity=self.identity, )
        return options

    def child_assent_obj(self, **kwargs):
        try:
            return self.assent_model_cls.objects.get(**kwargs)
        except self.assent_model_cls.DoesNotExist:
            return None

    @property
    def child_assents(self):
        wrapped_entries = []
        if getattr(self, 'consent_model_obj', None):
            """
            consent_model_obj is version 1, 2 or 3
            """

            # set was used, to get care giver child consent in v1 or v2
            caregiver_child_consents = self.consent_model_obj.caregiverchildconsent_set \
                .only('child_age_at_enrollment', 'is_eligible') \
                .filter(is_eligible=True, child_age_at_enrollment__gte=7)

            for caregiver_child_consent in caregiver_child_consents:
                model_obj = self.child_assent_model_obj(caregiver_child_consent) or \
                            self.assent_model_cls(
                                **self.create_child_assent_options(caregiver_child_consent))
                # create options based on caregiverchildconsent, which is either
                # version 1 or version 2

                wrapped_entries.append(ChildAssentModelWrapper(model_obj))
        return wrapped_entries

    def child_assents_exists(self) -> bool:

        exists_conditions = list()

        if getattr(self, 'consent_model_obj', None):
            caregiver_child_consents = self.consent_model_obj.caregiverchildconsent_set \
                .only('child_age_at_enrollment', 'is_eligible') \
                .filter(is_eligible=True,
                        child_age_at_enrollment__gte=7,
                        child_age_at_enrollment__lt=18)

            for caregiver_child_consent in caregiver_child_consents:
                model_objs = ChildAssent.objects.filter(
                    subject_identifier=caregiver_child_consent.subject_identifier).exists()
                exists_conditions.append(model_objs)

        return all(exists_conditions)

    def create_child_assent_options(self, caregiverchildconsent):

        # if hasattr(caregiverchildconsent, 'first_name')
        first_name = caregiverchildconsent.first_name
        last_name = caregiverchildconsent.last_name
        initials = self.set_initials(first_name, last_name)
        version = caregiverchildconsent.version
        options = dict(
            screening_identifier=self.screening_identifier,
            subject_identifier=caregiverchildconsent.subject_identifier,
            first_name=first_name,
            last_name=last_name,
            initials=initials,
            version=version,
            gender=caregiverchildconsent.gender,
            identity=caregiverchildconsent.identity,
            identity_type=caregiverchildconsent.identity_type,
            confirm_identity=caregiverchildconsent.confirm_identity,
            dob=caregiverchildconsent.child_dob)
        return options

    def child_assent_options(self, caregiverchildconsent):
        first_name = caregiverchildconsent.first_name
        last_name = caregiverchildconsent.last_name
        version = caregiverchildconsent.version
        options = dict(
            screening_identifier=self.screening_identifier,
            first_name=first_name,
            last_name=last_name,
            version=version,
            identity=caregiverchildconsent.identity)
        return options

    def child_assent_model_obj(self, caregiverchildconsent):
        try:
            return self.assent_model_cls.objects.get(
                subject_identifier=caregiverchildconsent.subject_identifier,
                version=caregiverchildconsent.version)
        except self.assent_model_cls.DoesNotExist:
            return None

    @property
    def child_age(self):
        if self.assent_model_obj:
            birth_date = self.assent_model_obj.dob
            difference = relativedelta(get_utcnow().date(), birth_date)
            months = 0
            if difference.years > 0:
                months = difference.years * 12
            years = round((months + difference.months) / 12, 2)
            return years
        return 0

    @property
    def child_assents_qs(self):
        if getattr(self, 'consent_model_obj', None):
            identities = self.consent_model_obj.caregiverchildconsent_set.values_list(
                'identity', flat=True)
            return self.assent_model_cls.objects.filter(identity__in=identities)

    @property
    def assents_eligibility(self):
        assent_eligible = True
        if self.child_assents_qs:
            assents_eligible = self.child_assents_qs.filter(is_eligible=True)
            if not assents_eligible:
                assent_eligible = False
        return assent_eligible

    @property
    def assents_ineligible(self):
        return self.child_assents_qs.filter(is_eligible=False)
