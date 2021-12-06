from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist
from .child_birth_model_wrapper import ChildBirthModelWrapper


class ChildBirthModelWrapperMixin:

    child_birth_model_wrapper_cls = ChildBirthModelWrapper

    @property
    def child_birth_cls(self):
        return django_apps.get_model('flourish_child.childbirth')

    @property
    def child_birth_obj(self):
        """Returns a child birth model instance or None.
        """

        try:
            return self.child_birth_cls.objects.get(
                subject_identifier=self.object.subject_identifier)
        except ObjectDoesNotExist:
            return None

    @property
    def child_birth(self):
        """"Returns a wrapped saved or unsaved child birth
        """

        model_obj = self.child_birth_obj or self.child_birth_cls(
            **self.childbirth_options)

        return self.child_birth_model_wrapper_cls(model_obj=model_obj)

    @property
    def childbirth_options(self):
        options = dict(
            subject_identifier=self.object.subject_identifier)
        return options
