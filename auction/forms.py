from django.forms import ModelForm
from .models import AddUriToArrayForm
from django import forms

class AddUriToArray(forms.Form):
        name = forms.CharField(max_length=30)
        image = forms.ImageField()

        def clean(self):
            cleaned_data = super().clean()
            name = self.cleaned_data.get('name')
            image = cleaned_data.get('image')
            return cleaned_data
        