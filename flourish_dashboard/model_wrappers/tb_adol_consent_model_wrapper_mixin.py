from datetime import datetime

from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from django.utils.timezone import make_aware
import pytz

from edc_consent.site_consents import site_consents

from .tb_adol_consent_model_wrapper import TbAdolConsentModelWrapper


class TbAdolConsentModelWrapperMixin:

    adol_consent_model_wrapper_cls = TbAdolConsentModelWrapper
    
    child_consent_model = 'flourish_caregiver.caregiverchildconsent'
    
    @property
    def child_consent_model_cls(self):
        return django_apps.get_model(self.child_consent_model)

    @property
    def tb_adol_consent_model_obj(self):
        """Returns a tb adolescent consent model instance or None.
        """
        try:
            return self.tb_adol_consent_cls.objects.get(
                **self.tb_adol_consent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def tb_adol_consent(self):
        """"Returns a wrapped saved or unsaved tb adolescent consent
        """
        model_obj = self.tb_adol_consent_model_obj or self.tb_adol_consent_cls(
            **self.create_tb_adol_consent_options)
        return TbAdolConsentModelWrapper(model_obj=model_obj)

    @property
    def tb_adol_consent_cls(self):
        return django_apps.get_model('flourish_caregiver.tbadolconsent')
    
    @property
    def child_consent_obj(self):

        try:
            
            consent_obj = self.child_consent_model_cls.objects.filter(
                subject_identifier__istartswith=self.object.subject_identifier
            ).latest('consent_datetime')
            
        except self.child_consent_model_cls.DoesNotExist:
            pass
        else:
            return consent_obj 
    

    @property
    def create_tb_adol_consent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted tb adolescent consent model instance.
        """
        
        data = dict()
        
        if self.child_consent_obj:
        
            data = dict(
                adol_firstname = self.child_consent_obj.first_name,
                adol_lastname = self.child_consent_obj.last_name,
                adol_gender = self.child_consent_obj.gender,
                adol_dob = self.child_consent_obj.child_dob)
            
            
    
                
        options = dict(
            subject_identifier=self.object.subject_identifier,
            version=self.tb_consent_version,
            first_name=self.object.first_name,
            last_name=self.object.last_name,
            initials=self.object.initials,
            dob=self.object.dob,
            identity=self.object.identity,
            identity_type=self.object.identity_type,
            language=self.object.language,
            is_literate=self.object.is_literate,
            witness_name=self.object.witness_name,
            is_dob_estimated=self.object.is_dob_estimated,
            confirm_identity=self.object.confirm_identity,
            **data)
        
        return options

    @property
    def tb_adol_consent_options(self):
        """Returns a dictionary of options to get an existing
         tb adolescent consent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier,
            version=self.tb_adol_consent_version,
            )
        return options

    @property
    def tb_adol_consent_version(self):
        current_datetime = datetime.now()
        tz = pytz.timezone('Africa/Gaborone')
        consent_datetime = make_aware(current_datetime, tz, True)
        consent = site_consents.get_consent_for_period(
            self.adol_consent_model_wrapper_cls.model,
            report_datetime=consent_datetime)
        return consent.version
