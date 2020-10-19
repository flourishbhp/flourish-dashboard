from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormMixin

from django.http import HttpResponseRedirect
from django.shortcuts import render

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

#     def post(self,request, *args, **kwargs):
#         form = WorklistCreateListForm(request.POST)
#         if form.is_valid():
#             print('&&&&&&&&&&&&&')

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        print(request.POST, '%%%%%%5')
        if form.is_valid():
            print('################### we a re all good')
            print(form, '++++++++++')
            identifiers = form.cleaned_data['identifiers']
            # <process form cleaned data>
            return render(request, self.template_name, {'form': form, 'identifiers': identifiers})
        else:
            print(form.errors, '@@@@@@@@@@@@@@@@@@@@@@')

        return render(request, self.template_name, {'form': form})

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
