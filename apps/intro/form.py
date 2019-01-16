from django import forms

class StaffForm(forms.Form):
    name = forms.CharField(max_length=128)
    team = forms.ChoiceField(choices=(('site', 'site'),('graphic', 'graphic'), ('game design', 'game design'),('infrastructure','infrastructure'),('test','test'),('content','content'),('server and client','server and client')))
    image = forms.FileField()
