from django.core.management.base import BaseCommand, CommandError
from apps.game.models import Challenge


class Command(BaseCommand):
    help = 'Creates a seeding league for the specified challenge.'

    def add_arguments(self, parser):
        parser.add_argument('challenge_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for challenge_id in options['challenge_id']:
            try:
                challenge = Challenge.objects.get(pk=challenge_id)
            except Challenge.DoesNotExist:
                raise CommandError('Poll "%s" does not exist.' % challenge_id)

            team_pcs = challenge.sta

            self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s".' % challenge_id))
