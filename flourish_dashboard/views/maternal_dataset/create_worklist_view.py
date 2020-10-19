from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormMixin

from edc_base.view_mixins import EdcBaseViewMixin
from edc_navbar import NavbarViewMixin

from ...forms import WorklistCreateListForm


class CreateWorklistView(
        EdcBaseViewMixin, NavbarViewMixin,
        FormMixin, TemplateView):

    template_name = 'flourish_dashboard/maternal_dataset/test.html'
    form_class = WorklistCreateListForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print('DDDDDDDDDDDDDDDDDDDDDDDDDDDDDD&&&&&&&&&&&&&&&&7    ')
        context.update()
        return context

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        identifier_list = []
        for item in form.POST.getlist('identifiers'):
            identifier_list.append(item)
        print(identifier_list)
        return super().form_valid(form)

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
