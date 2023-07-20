from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_constants.constants import YES
from django.db.models.functions import Lower
from .tb_adol_screening_model_wrapper import TbAdolScreeningModelWrapper


class TbAdolScreeningModelWrapperMixin:

    adol_screening_model_wrapper_cls = TbAdolScreeningModelWrapper

    caregiver_child_consent_model = 'flourish_caregiver.caregiverchildconsent'

    tb_adol_assent_model = 'flourish_child.tbadolassent'

    tb_adol_consent_model = 'flourish_caregiver.tbadolconsent'

    child_dataset_model = 'flourish_child.childdataset'

    @property
    def child_dataset_cls(self):
        return django_apps.get_model(self.child_dataset_model)


    @property
    def tb_adol_assent_cls(self):
        return django_apps.get_model(self.tb_adol_assent_model)

    @property
    def caregiver_child_consent_cls(self):
        return django_apps.get_model(self.caregiver_child_consent_model)
    
    @property
    def tb_adol_screening_model_obj(self):
        """Returns a tb adolescent screening model instance or None.
        """
        try:
            return self.tb_adol_screening_cls.objects.get(
                **self.tb_adol_screening_options)
        except ObjectDoesNotExist:
            return None

    @property
    def tb_adol_screening(self):
        """"Returns a wrapped saved or unsaved tb adolescent screening
        """
        model_obj = self.tb_adol_screening_model_obj or self.tb_adol_screening_cls(
            **self.create_tb_adol_screening_options)
        return TbAdolScreeningModelWrapper(model_obj=model_obj)

    @property
    def tb_adol_screening_cls(self):
        return django_apps.get_model('flourish_caregiver.tbadoleligibility')
    
    @property
    def tb_adol_consent_cls(self):
        return django_apps.get_model(self.tb_adol_consent_model)

    @property
    def tb_adol_eligibility(self):
        if self.tb_adol_screening_model_obj:
            return self.tb_adol_screening_model_obj.tb_adol_participation == YES
        
    @property
    def total_huu_adol_limits(self):
        """
        Returns a count down out of 25 HUU participant being enrolled in tb adol
        """

        subject_identifiers = self.tb_adol_assent_cls.objects.filter(
                is_eligible=True).values_list('subject_identifier', flat=True).distinct()
        
        study_child_identifiers = self.caregiver_child_consent_cls.objects.filter(
            subject_identifier__in=subject_identifiers
        ).values_list('study_child_identifier', flat=True).distinct()
        

        unexposed_adolencent = self.child_dataset_cls.objects.annotate(
                    infant_hiv_exposed_lower=Lower('infant_hiv_exposed')
                ).filter(
            infant_hiv_exposed_lower='unexposed', study_child_identifier__in=study_child_identifiers).count()
        
        return 25 - unexposed_adolencent

    @property
    def create_tb_adol_screening_options(self):
        """Returns a dictionary of options to create a new
        unpersisted tb adolescent screening model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            )
        return options

    @property
    def tb_adol_screening_options(self):
        """Returns a dictionary of options to get an existing
         tb adolescent screening model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            )
        return options
