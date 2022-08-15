from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_base.utils import age, get_utcnow


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
        years = None
        if self.object.child_dob:
            birth_date = self.object.child_dob
            child_age = age(birth_date, get_utcnow())
            months = 0
            if child_age.years > 0:
                months = child_age.years * 12
            years = round((months + child_age.months) / 12, 2)
        return years if years else 0

    @property
    def caregiverchildconsent_obj(self):
        """Returns a caregiver child consent model instance or None.
        """
        try:
            # was returning non with caregiverchildconsent_options, so subject identifier
            # and version was used instead
            return self.caregiver_childconsent_cls.objects.get(
                subject_identifier=self.subject_identifier,
                version=self.child_consent_version
            )
        except self.caregiver_childconsent_cls.DoesNotExist:
            return None

    @property
    def caregiverchildconsent(self):
        """"Returns a wrapped saved or unsaved consent on behalf of child
        """
        model_obj = self.caregiverchildconsent_obj or self.child_consent_model_wrapper_cls(
            **self.caregiverchildconsent_options)
        if self.child_consent_model_wrapper_cls:
            return self.child_consent_model_wrapper_cls(model_obj=model_obj)
        else:
            return self.__class__(model_obj=model_obj)

    @property
    def caregiverchildconsent_options(self):
        options = dict(
            subject_consent=self.object.subject_consent,
            identity=self.identity or '',
            version=self.child_consent_version)
        return options
