from django import forms


class StaffForm(forms.Form):
    name = forms.CharField(max_length=128)
    team = forms.ChoiceField(choices=(('Site', 'Site'), ('Graphic', 'Graphic'),
                                      ('Game Design', 'Game Design'), ('Head', 'Head'),
                                      ('Infrastructure', 'Infrastructure'), ('Content', 'Content'),
                                      ('Server and Client', 'Server and Client'), ('Others', 'Others'),
                                      ('Branding', 'Branding'), ('Design', 'Design')))
    image = forms.FileField()
