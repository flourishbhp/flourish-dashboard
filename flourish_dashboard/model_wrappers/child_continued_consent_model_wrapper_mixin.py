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
                **self.child_continued_consent_options).latest(
                    'consent_datetime')
        except ObjectDoesNotExist:
            return None

    @property
    def child_continued_consent(self):
        """"Returns a wrapped saved or unsaved child continued consent
        """
        model_obj = (self.child_continued_consent_model_obj or
                     self.child_continued_consent_cls(
                         **self.create_child_continued_consent_options))
        return self.child_continued_consent_model_wrapper_cls(
            model_obj=model_obj)

    @property
    def child_continued_consent_version(self):
        child_consent_version_model_cls = django_apps.get_model(
            'flourish_child.childconsentversion')
        try:
            model_obj = child_consent_version_model_cls.objects.get(
                subject_identifier=self.subject_identifier)
        except child_consent_version_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def child_continued_consents(self):
        """
            Returns wrapped instances of the child continued consents.
            If there is no current version of the consent, include an
            unsaved consent to be completed by user for recent version.
        """
        wrapped_entries = []
        child_consents = self.child_continued_consent_cls.objects.filter(
            subject_identifier=self.subject_identifier)

        current_version = getattr(
            self.child_continued_consent_version, 'version', None)
        is_current = False
        for model_obj in child_consents:
            if model_obj.version == current_version:
                is_current = True
            wrapped_entries.append(
                self.child_continued_consent_model_wrapper_cls(model_obj))
        if current_version and not is_current:
            unsaved_model_obj = self.child_continued_consent_cls(
                **self.create_child_continued_consent_options)
            wrapped_entries.append(
                self.child_continued_consent_model_wrapper_cls(
                    unsaved_model_obj))
        return wrapped_entries

    @property
    def caregiverchildconsent(self):
        child_consent_model_cls = django_apps.get_model(
            'flourish_caregiver.caregiverchildconsent')
        try:
            model_obj = child_consent_model_cls.objects.filter(
                subject_identifier=self.subject_identifier).latest(
                    'consent_datetime')
        except child_consent_model_cls.DoesNotExist:
            return None
        else:
            return model_obj

    @property
    def create_child_continued_consent_options(self):
        """
            Returns a dictionary of options to create a new
            unpersisted child continued consent model instance.
        """

        first_name = getattr(self.caregiverchildconsent, 'first_name', None)
        last_name = getattr(self.caregiverchildconsent, 'last_name', None)
        initials = self.set_initials(first_name, last_name)

        current_version = getattr(
            self.child_continued_consent_version, 'version', None)

        options = dict(
            subject_identifier=self.subject_identifier,
            first_name=first_name,
            last_name=last_name,
            initials=initials,
            gender=getattr(self.caregiverchildconsent, 'gender', None),
            identity=getattr(self.caregiverchildconsent, 'identity', None),
            identity_type=getattr(
                self.caregiverchildconsent, 'identity_type', None),
            confirm_identity=getattr(
                self.caregiverchildconsent, 'confirm_identity', None),
            dob=getattr(self.caregiverchildconsent, 'child_dob', None),
            version=current_version)
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
