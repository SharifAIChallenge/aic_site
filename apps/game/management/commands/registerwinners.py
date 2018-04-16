from random import shuffle

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.game.models import Challenge, TeamParticipatesChallenge, Competition, Map
from apps.game.models.challenge import UserAcceptsTeamInChallenge
from apps.game.utils import get_scoreboard_table_tag


class Command(BaseCommand):
    help = 'Creates a seeding league for the specified challenge.'

    def add_arguments(self, parser):
        parser.add_argument(
            'challenge_id',
            type=int,
            help='The challenge to register users in'
        )
        parser.add_argument(
            'tag',
            type=str,
            help='Tag of the reference league'
        )
        parser.add_argument(
            'size',
            type=int,
            help='Number of teams to select'
        )

    def handle(self, *args, **options):
        size = options['size']
        if size < 1:
            raise CommandError('group_size should be more than 0')

        teams_status = get_scoreboard_table_tag(
            timezone.now(),
            options['tag'])[0:size]

        teams = [team_status['team'] for team_status in teams_status]

        try:
            challenge = Challenge.objects.get(id=options['challenge_id'])
        except Challenge.DoesNotExist:
            raise CommandError('Invalid challenge id')

        for team in teams:
            team_pc = TeamParticipatesChallenge.objects.create(team=team, challenge=challenge)
            for participation in team.participants.all():
                UserAcceptsTeamInChallenge.objects.create(
                    user=participation.user,
                    team=team_pc
                )
                participation.user.profile.panel_active_teampc = team_pc
                participation.user.profile.save()

        self.stdout.write(self.style.SUCCESS('Successfully registered users.'))
