from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .child_continued_consent_model_wrapper import ChildContinuedConsentModelWrapper


class ChildContinuedConsentModelWrapperMixin:

    child_continued_consent_model_wrapper_cls = ChildContinuedConsentModelWrapper

    @property
    def child_continued_consent_model_obj(self):
        """Returns a child continued consent model instance or None.
        """
        try:
            return self.child_continued_consent_cls.objects.get(
                **self.child_continued_consent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def child_continued_consent(self):
        """"Returns a wrapped saved or unsaved child continued consent
        """
        model_obj = self.child_continued_consent_model_obj or self.child_continued_consent_cls(
            **self.create_child_continued_consent_options)
        return self.child_continued_consent_model_wrapper_cls(model_obj=model_obj)

    @property
    def child_continued_consent_cls(self):
        return django_apps.get_model('flourish_child.childcontinuedconsent')

    @property
    def child_continued_consent_model_obj(self):
        """Returns a child continued consent model instance or None.
        """
        try:
            return self.child_continued_consent_cls.objects.filter(
                **self.child_continued_consent_options).latest('consent_datetime')
        except ObjectDoesNotExist:
            return None

    @property
    def child_continued_consent(self):
        """"Returns a wrapped saved or unsaved child continued consent
        """
        model_obj = self.child_continued_consent_model_obj or self.child_continued_consent_cls(
            **self.child_continued_consent_options)
        return self.child_continued_consent_model_wrapper_cls(model_obj=model_obj)

    def get_model_obj_by_version(self, caregiverchildconsent):
        try:
            return self.child_continued_consent_cls.objects.get(
                subject_identifier=caregiverchildconsent.subject_identifier,
                version=caregiverchildconsent.version)
        except self.child_continued_consent_cls.DoesNotExist:
            return None

    @property
    def create_child_continued_consent_options(self):
        """Returns a dictionary of options to create a new
        unpersisted child continued consent model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier, )
        return options

    @property
    def child_continued_consent_options(self):
        """Returns a dictionary of options to get an existing
         child continued consent model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier, )
        return options
