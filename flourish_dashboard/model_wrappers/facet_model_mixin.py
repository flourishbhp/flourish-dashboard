from django.apps import apps as django_apps

class FacetModelWrapperMixin:

    facet_screening_model = 'flourish_facet.facetsubjectscreening'

    @property
    def facet_screening_cls(self):
        return django_apps.get_model(self.facet_screening_model)
        
    @property
    def facet_screening_obj(self):
        try:
            screen_obj = self.facet_screening_cls.objects.get(
                subject_identifier = self.subject_identifier
            )

        except self.facet_screening_cls.DoesNotExist:
            pass
        else:
            return screen_obj