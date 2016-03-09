from django import forms

class QueryForm(forms.Form):
	q = forms.CharField(label='Query', max_length=100)