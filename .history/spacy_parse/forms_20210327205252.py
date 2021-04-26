from django import forms
from django.contrib.postgres.forms import SimpleArrayField

class TraitValuesForm(forms.Form):
    traitvalues = SimpleArrayField()
    class Meta:
        fields = ['traitvalues']
