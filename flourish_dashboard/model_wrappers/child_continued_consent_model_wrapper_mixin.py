from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from edc_base.utils import age, get_utcnow

from .child_continued_consent_model_wrapper import ChildContinuedConsentModelWrapper


class ChildContinuedConsentModelWrapperMixin:
    child_continued_consent_model_wrapper_cls = ChildContinuedConsentModelWrapper

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
    def child_continued_consents(self):
        wrapped_entries = []
        if getattr(self, 'consent_model_obj', None):
            caregiver_child_consents = self.consent_model_obj.caregiverchildconsent_set.filter(
                is_eligible=True, child_dob__isnull=False)

            for child_consent in caregiver_child_consents:
                child_dob = getattr(child_consent, 'child_dob', None)
                _child_age = self._child_current_age(child_dob)
                if _child_age < 18:
                    continue
                model_obj = (self.get_model_obj_by_version(child_consent) or
                             self.child_continued_consent_cls(
                                 **self.create_child_continued_consent_options(
                                    child_consent)))

                wrapped_entries.append(
                    self.child_continued_consent_model_wrapper_cls(model_obj))
        return wrapped_entries

    def create_child_continued_consent_options(self, caregiverchildconsent):
        """Returns a dictionary of options to create a new
        unpersisted child continued consent model instance.
        """
        # if hasattr(caregiverchildconsent, 'first_name')
        first_name = caregiverchildconsent.first_name
        last_name = caregiverchildconsent.last_name
        initials = self.set_initials(first_name, last_name)
        version = caregiverchildconsent.version

        options = dict(
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

    @property
    def child_continued_consent_options(self):
        """Returns a dictionary of options to get an existing
         child continued consent model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier, )
        return options

    def _child_current_age(self, child_dob):
        _age = age(child_dob, get_utcnow().date())
        return _age.years + (_age.months / 12)
