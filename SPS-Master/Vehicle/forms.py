from django import forms
 
class SearchForm(forms.Form):
    search_title = forms.CharField(label='Search Vehicle',max_length=100,widget=forms.TextInput(attrs={'class':'form-control'}))