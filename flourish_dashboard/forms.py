from django import forms
from django.apps import apps as django_apps
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit


class LocatorLogReportForm(forms.Form):

    username = forms.ChoiceField(
        label='Username',
        widget=forms.Select())

    start_date = forms.DateField(
        label='Start date',
        widget=forms.TextInput(
            attrs={'type': 'date'}))

    end_date = forms.DateField(
        label='End date',
        widget=forms.TextInput(
            attrs={'type': 'date'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].choices = self.users
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'assign_participant'
        self.helper.form_action = 'flourish_follow:home_url'

        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(
            'username',
            'start_date',
            'end_date',
            Submit('submit', u'Assign', css_class="btn btn-sm btn-default"),
        )

    @property
    def users(self):
        """Return all users to be on the report.
        """
        assignable_users_choices = (('---', 'None'),)
        user = django_apps.get_model('auth.user')
        app_config = django_apps.get_app_config('edc_data_manager')
        assignable_users_group = app_config.assignable_users_group
        try:
            Group.objects.get(name=assignable_users_group)
        except Group.DoesNotExist:
            Group.objects.create(name=assignable_users_group)
        assignable_users = user.objects.filter(
            groups__name=assignable_users_group)
        extra_choices = ()
        if app_config.extra_assignee_choices:
            for _, value in app_config.extra_assignee_choices.items():
                extra_choices += (value[0],)
        for assignable_user in assignable_users:
            username = assignable_user.username
            if not assignable_user.first_name:
                raise ValidationError(
                    f'The user {username} needs to set their first name.')
            if not assignable_user.last_name:
                raise ValidationError(
                    f"The user {username} needs to set their last name.")
            full_name = (f'{assignable_user.first_name} '
                         f'{assignable_user.last_name}')
            assignable_users_choices += ((username, full_name),)
        if extra_choices:
            assignable_users_choices += extra_choices
        return assignable_users_choices
