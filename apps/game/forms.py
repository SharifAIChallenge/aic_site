from django.forms import ModelForm
from apps.game.models import Map
from django.utils.translation import ugettext_lazy as _


class MapForm(ModelForm):
    class Meta:
        model = Map
        fields = ['file', 'name']

    def is_valid(self):
        valid = super(MapForm, self).is_valid()
        if not valid:
            return valid
        if self.instance.file.size > 524288:
            self.errors['file'] = _('Max acceptable file size is 500kb')
            return False
        return True
