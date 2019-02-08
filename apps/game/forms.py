from django.forms import ModelForm
from apps.game.models import Map

class MapForm(ModelForm):
    class Meta:
        model = Map
        fields = ['file', 'name']

