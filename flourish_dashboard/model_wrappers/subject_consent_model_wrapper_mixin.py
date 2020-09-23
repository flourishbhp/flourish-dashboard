from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .subject_consent_model_wrapper import SubjectConsentModelWrapper

class SubjectConsentModelWrapperMixin:
    
    subject_consent_wrapper_cls = SubjectConsentModelWrapper
    
    @property
    def subject_identifier(self):
        if self.subject_consent_obj:
            return self.subject_consent_obj.subject_identifier
        return None

    @property
    def subject_consent_obj(self):
        """Returns a maternal model instance or None.
        """
        try:
            return self.subject_consent_cls.objects.get(
                **self.subject_consent_options)
        except ObjectDoesNotExist:
            return None
        
    @property
    def subject_consent(self):
        """"Returns a wrapped saved or unsaved subject consent
        """
        model_obj = self.subject_consent_obj or self.subject_consent_cls(
            **self.subject_consent_options)
        return self.subject_consent_wrapper_cls(model_obj=model_obj)


    @property
    def subject_consent_cls(self):
        return django_apps.get_model('flourish_maternal.subjectconsent')

    @property
    def create_subject_consent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted subject consent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier)
        return options

    @property
    def subject_consent_options(self):
        """Returns a dictionary of options to get an existing
        subject consent model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier)
        return options
