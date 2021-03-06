from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist


class CaregiverChildConsentModelWrapperMixin:

    child_consent_model_wrapper_cls = None

    @property
    def subject_consent(self):
        return self.object.subject_consent

    @property
    def caregiver_childconsent_cls(self):
        return django_apps.get_model(self.model)

    @property
    def screening_identifier(self):
        return self.object.subject_consent.screening_identifier

    @property
    def child_age(self):
        return int(self.object.child_age_at_enrollment)

    @property
    def caregiverchildconsent_obj(self):
        """Returns a caregiver consent model instance or None.
        """
        try:
            return self.caregiver_childconsent_cls.objects.get(
                **self.caregiverchildconsent_options)
        except ObjectDoesNotExist:
            return None

    @property
    def caregiverchildconsent(self):
        """"Returns a wrapped saved or unsaved consent on behalf of child
        """
        model_obj = self.caregiverchildconsent_obj or self.child_consent_model_wrapper_cls(
            **self.caregiverchildconsent_options)
        return self.child_consent_model_wrapper_cls(model_obj=model_obj)

    @property
    def caregiverchildconsent_options(self):
        options = dict(
            subject_consent=self.object.subject_consent,
            identity=self.identity,
            version=self.consent_version)
        return options
