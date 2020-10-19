from django import forms


class WorklistCreateListForm(forms.Form):

    identifiers = forms.CharField()
