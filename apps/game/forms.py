from django.forms import ModelForm
from django.utils import timezone

from aic_site.settings.base import UPLOAD_MAP_TIME_DELTA
from apps.game.models import Map
from django.utils.translation import ugettext_lazy as _


class MapForm(ModelForm):
    class Meta:
        model = Map
        fields = ['file', 'name']

    def is_valid(self, team):
        team_maps = Map.objects.filter(team=team)
        for m in team_maps:
            if timezone.now()-m.time_created < timezone.timedelta(hours=UPLOAD_MAP_TIME_DELTA):
                self.errors[''] = _('You can not upload a map right now. You have uploaded a map recently!')
                return False
        valid = super(MapForm, self).is_valid()
        if not valid:
            return valid
        if self.instance.file.size > 524288:
            self.errors['file'] = _('Max acceptable file size is 500kb')
            return False

        return True
