from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .child_consent_version_model_wrapper import ChildConsentVersionModelWrapper


class ChildConsentVersionModelWrapperMixin:

    child_consent_version_model_wrapper_cls = ChildConsentVersionModelWrapper

    @property
    def child_continued_consent_version_model_obj(self):
        """
            Returns a child consent version model instance or None.
        """
        try:
            return self.consent_version_cls.objects.get(
                **self.consent_version_options)
        except ObjectDoesNotExist:
            return None

    @property
    def child_continued_consent_version(self):
        """Returns a wrapped saved or unsaved consent version.
        """

        model_obj = (self.child_continued_consent_version_model_obj or
                     self.child_continued_consent_version_cls(
                         **self.child_continued_consent_version_options))

        return self.child_consent_version_model_wrapper_cls(
            model_obj=model_obj)

    @property
    def child_continued_consent_version_cls(self):
        return django_apps.get_model(
            'flourish_child.childconsentversion')

    @property
    def child_continued_consent_version_options(self):
        """
            Returns a dictionary of options to create a new
            unpersisted Child consent version model instance.
        """
        options = dict(
            subject_identifier=self.object.screening_identifier,
        )
        return options
