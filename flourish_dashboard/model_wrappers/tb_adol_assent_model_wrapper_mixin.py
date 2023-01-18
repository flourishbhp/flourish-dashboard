from dateutil.relativedelta import relativedelta
from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from edc_base.utils import get_utcnow, age

from .tb_adol_assent_model_wrapper import TbAdolAssentModelWrapper


class TbAdolChildAssentModelWrapperMixin:
    tb_adol_assent_model_wrapper_cls = TbAdolAssentModelWrapper

    @property
    def tb_adol_assent_model_cls(self):
        return django_apps.get_model('flourish_child.tbadolassent')

    @property
    def consent_version_cls(self):
        return django_apps.get_model('flourish_caregiver.flourishconsentversion')

    @property
    def subject_consent_cls(self):
        return django_apps.get_model('flourish_caregiver.subjectconsent')

    @property
    def tb_adol_assent_model_obj(self):
        """Returns a child assent model instance or None.
        """
        try:
            return self.tb_adol_assent_model_cls.objects.get(
                **self.tb_adol_assent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def tb_adol_assent(self):
        """"Returns a wrapped saved or unsaved child assent
        """
        if 10 <= self.adol_age <= 17:

            model_obj = self.tb_adol_assent_model_obj or self.tb_adol_assent_model_cls(
                **self.create_tb_adol_assent_options(self.caregiverchildconsent_obj))

            return TbAdolAssentModelWrapper(model_obj=model_obj)

    @property
    def current_version(self):
        """
        Get the version of the current passed consent
        """
        if self.consent_model_obj:
            return self.consent_model_obj.version

    @property
    def create_tb_adol_assent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted child assent model instance.
        """

        options = dict(
            screening_identifier=self.screening_identifier)
        return options

    @property
    def tb_adol_assent_options(self):
        """Returns a dictionary of options to get an existing
         child assent model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier,
            identity=self.identity,)
        return options

    def tb_adol_assent_obj(self, **kwargs):
        try:
            return self.tb_adol_assent_model_cls.objects.get(**kwargs)
        except self.tb_adol_assent_model_cls.DoesNotExist:
            return None

    @property
    def tb_adol_assents(self):
        
        wrapped_entries = []
        if getattr(self, 'consent_model_obj', None):
            """
            consent_model_obj is version 1 or 2
            """

            # set was used, to get care giver child consent in v1 or v2
            caregiverchildconsents = self.consent_model_obj.caregiverchildconsent_set \
                .only('child_age_at_enrollment', 'is_eligible') \
                .filter(is_eligible=True)

            for caregiverchildconsent in caregiverchildconsents:
                
                child_age = age(caregiverchildconsent.child_dob, get_utcnow()).years
                
                if 10 <= child_age <= 17:
                    model_obj = self.get_tb_adol_assent_model_obj(caregiverchildconsent) or \
                                self.tb_adol_assent_model_cls(
                                    **self.create_tb_adol_assent_options(caregiverchildconsent))

                wrapped_entries.append(TbAdolAssentModelWrapper(model_obj))
        return wrapped_entries
    
    def tb_adol_child_assents(self):
        wrapped_entries = []
        if getattr(self, 'consent_model_obj', None):
            """
            consent_model_obj is version 1 or 2
            """

            # set was used, to get care giver child consent in v1 or v2
            caregiverchildconsents = self.consent_model_obj.caregiverchildconsent_set \
                .only('child_age_at_enrollment', 'is_eligible') \
                .filter(is_eligible=True, child_age_at_enrollment__gte=7)

            for caregiverchildconsent in caregiverchildconsents:
                model_obj = self.get_tb_adol_assent_model_obj(caregiverchildconsent) or \
                            self.tb_adol_assent_model_cls(
                                **self.create_tb_adol_assent_options(caregiverchildconsent))
                # create options based on caregiverchildconsent, which is either version 1 or version 2

                wrapped_entries.append(TbAdolAssentModelWrapper(model_obj))
        return wrapped_entries
    

    def tb_adol_assents_exists(self) -> bool:

        exists_conditions = list()

        if getattr(self, 'consent_model_obj', None):
            caregiverchildconsents = self.consent_model_obj.caregiverchildconsent_set \
                .only('child_age_at_enrollment', 'is_eligible') \
                .filter(is_eligible=True,
                        child_age_at_enrollment__gte=7,
                        child_age_at_enrollment__lt=18)

            for caregiver_childconsent in caregiverchildconsents:
                model_objs = self.tb_adol_assent_model_cls.objects.filter(
                    subject_identifier=caregiver_childconsent.subject_identifier).exists()
                exists_conditions.append(model_objs)

            return all(exists_conditions)

    def create_tb_adol_assent_options(self, caregiverchildconsent):

        # if hasattr(caregiverchildconsent, 'first_name')
        first_name = caregiverchildconsent.first_name
        last_name = caregiverchildconsent.last_name
        initials = self.set_initials(first_name, last_name)
        version = self.current_version

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

    def get_tb_adol_assent_options(self, caregiverchildconsent):
        first_name = caregiverchildconsent.first_name
        last_name = caregiverchildconsent.last_name
        version = self.current_version

        options = dict(
            screening_identifier=self.screening_identifier,
            first_name=first_name,
            last_name=last_name,
            version=version,
            identity=caregiverchildconsent.identity)
        return options

    def get_tb_adol_assent_model_obj(self, caregiverchildconsent):
        try:
            return self.tb_adol_assent_model_cls.objects.get(subject_identifier=caregiverchildconsent.subject_identifier)
        except self.tb_adol_assent_model_cls.DoesNotExist:
            return None

    @property
    def adol_age(self):
        if self.tb_adol_assent_model_obj:
            birth_date = self.tb_adol_assent_model_obj.dob
            difference = relativedelta(get_utcnow().date(), birth_date)
            months = 0
            if difference.years > 0:
                months = difference.years * 12
            years = round((months + difference.months) / 12, 2)
            return years
        return 0

    @property
    def tb_adol_assents_qs(self):
        if getattr(self, 'consent_model_obj', None):
            identities = self.consent_model_obj.caregiverchildconsent_set.values_list(
                'identity', flat=True)
            return self.tb_adol_assent_model_cls.objects.filter(identity__in=identities)

    @property
    def tb_adol_assents_eligibility(self):
        assent_eligible = True
        if self.tb_adol_assents_qs:
            assents_eligible = self.tb_adol_assents_qs.filter(is_eligible=True)
            if not assents_eligible:
                assent_eligible = False
        return assent_eligible

    @property
    def tb_adol_assents_ineligible(self):
        return self.tb_adol_assents_qs.filter(is_eligible=False)
