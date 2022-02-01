from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .child_offstudy_model_wrapper import ChildOffstudyModelWrapper


class ChildOffstudyModelWrapperMixin:
    child_offstudy_model_wrapper_cls = ChildOffstudyModelWrapper

    @property
    def child_offstudy_model_obj(self):
        """Returns a child offstudy model instance or None.
        """
        try:
            return self.child_offstudy_cls.objects.get(
                **self.child_offstudy_options)
        except ObjectDoesNotExist:
            return None

    @property
    def child_offstudy(self):
        """"Returns a wrapped saved or unsaved child offstudy
        """
        model_obj = self.child_offstudy_model_obj or \
                    self.child_offstudy_cls(
                        **self.create_child_offstudy_options
                    )
        return self.child_offstudy_model_wrapper_cls(model_obj=model_obj)

    @property
    def child_offstudy_cls(self):
        return django_apps.get_model('flourish_prn.childoffstudy')

    @property
    def create_child_offstudy_options(self):
        """Returns a dictionary of options to create a new
        unpersisted subject locator model instance.
        """
        options = dict(
            subject_identifier=self.subject_identifier)
        return options


    @property
    def child_offstudy_options(self):
        """Returns a dictionary of options to get an existing
         child offstudy model instance.
        """
        options = dict(
            subject_identifier=self.object.subject_identifier, )
        return options
