import django.forms as forms

class EditForm(forms.Form):
    short_name = forms.CharField()
    deleted = forms.BooleanField(required=False)
