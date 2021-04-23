from django import forms
from django.apps import apps as django_apps
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class LocatorLogReportForm(forms.Form):

    username = forms.ChoiceField(
        label='Username',
        required=False,
        widget=forms.Select())

    start_date = forms.DateField(
        label='Start date',
        required=False,
        widget=forms.TextInput(
            attrs={'type': 'date'}))

    end_date = forms.DateField(
        label='End date',
        required=False,
        widget=forms.TextInput(
            attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].choices = self.users
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_id = 'assign_participant'
        self.helper.form_action = 'flourish_dashboard:locator_report_url'

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'username',
            'start_date',
            'end_date',
            Submit('submit', u'Search', css_class="btn btn-sm btn-default"),
        )

    @property
    def users(self):
        """Return all users to be on the report.
        """
        locator_users_choices = ((None, 'Select User'),)
        user = django_apps.get_model('auth.user')
        locator_users_group = 'locator users'
        try:
            Group.objects.get(name=locator_users_group)
        except Group.DoesNotExist:
            Group.objects.create(name=locator_users_group)
        locator_users = user.objects.filter(
            groups__name=locator_users_group)
        for locator_user in locator_users:
            username = locator_user.username
            if not locator_user.first_name:
                raise ValidationError(
                    f'The user {username} needs to set their first name.')
            if not locator_user.last_name:
                raise ValidationError(
                    f"The user {username} needs to set their last name.")
            full_name = (f'{locator_user.first_name} '
                         f'{locator_user.last_name}')
            locator_users_choices += ((username, full_name),)
        return locator_users_choices
