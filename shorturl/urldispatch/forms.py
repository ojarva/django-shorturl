import django.forms as forms

class EditForm(forms.Form):
    short_name = forms.CharField()
    active = forms.BooleanField(required=False)
