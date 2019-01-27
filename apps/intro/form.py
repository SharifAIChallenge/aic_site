from django import forms

class StaffForm(forms.Form):
    name = forms.CharField(max_length=128)
    team = forms.ChoiceField(choices=(('executive','executive'),('site', 'site'),('graphic', 'graphic'), ('game design', 'game design'),('infrastructure','infrastructure'),('head','head'),('content','content'),('server and client','server and client'),('branding','branding'),('design','design')))
    image = forms.FileField()
