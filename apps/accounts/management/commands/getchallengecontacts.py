from random import shuffle

from django.core.management.base import BaseCommand, CommandError
from apps.game.models import Challenge, TeamParticipatesChallenge, Competition, Map
from apps.game.models.challenge import UserAcceptsTeamInChallenge
from apps.game.utils import get_scoreboard_table_tag


class Command(BaseCommand):
    help = 'Creates a seeding league for the specified challenge.'

    def add_arguments(self, parser):
        parser.add_argument(
            'challenge_id',
            type=int,
            help='The challenge to get its contact information'
        )

    def handle(self, *args, **options):
        try:
            challenge = Challenge.objects.get(id=options['challenge_id'])
        except Challenge.DoesNotExist:
            raise CommandError('Invalid challenge id')

        participations = challenge.teams.all().prefetch_related('team__participants__user__profile')

        print("Team Name,First Name, Last Name, Username,Phone,Email")

        for participation in participations:
            for participant in participation.team.participants.all():
                print('{},{},{},{},{},{}'.format(
                    participation.team.name,
                    participant.user.first_name,
                    participant.user.last_name,
                    participant.user.username,
                    participant.user.profile.phone_number,
                    participant.user.email
                ))

        # success
