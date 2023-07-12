# forms.py
from django import forms
from .models import *

directionChoices = {
	(True, 'Entry'),
	(False, 'Exit')
}

class photosform(forms.ModelForm):
	direction = forms.ChoiceField(
		widget=forms.RadioSelect,
		choices=directionChoices,
		initial=True
	)

	class Meta:
		model = photos
		fields = ['plate']
