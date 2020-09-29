from django.apps import apps as django_apps
from django.core.exceptions import ObjectDoesNotExist

from .maternal_locator_model_wrapper import MaternalLocatorModelWrapper


class MaternalLocatorModelWrapperMixin:
    
    locator_model_wrapper_cls = MaternalLocatorModelWrapper

    @property
    def screening_identifier(self):
        if self.locator_model_obj:
            return self.locator_model_obj.screening_identifier
        return None

    @property
    def locator_model_obj(self):
        """Returns a maternal locator model instance or None.
        """
        try:
            return self.maternal_locator_cls.objects.get(
                **self.maternal_locator_options)
        except ObjectDoesNotExist:
            return None
        
    @property
    def maternal_locator(self):
        """"Returns a wrapped saved or unsaved maternal locator
        """
        model_obj = self.locator_model_obj or self.maternal_locator_cls(
            **self.create_maternal_locator_options)
        return MaternalLocatorModelWrapper(model_obj=model_obj)

    @property
    def maternal_locator_cls(self):
        return django_apps.get_model('flourish_maternal.maternallocator')

    @property
    def create_maternal_locator_options(self):
        """Returns a dictionary of options to create a new
        unpersisted maternal locator model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier)
        return options
    
    @property
    def maternal_locator_options(self):
        """Returns a dictionary of options to get an existing
         maternal locator model instance.
        """
        options = dict(
            screening_identifier=self.object.screening_identifier)
        return options

