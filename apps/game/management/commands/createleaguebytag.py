from random import shuffle

from django.core.management.base import BaseCommand, CommandError
from apps.game.models import Challenge, TeamParticipatesChallenge, Competition, Map
from apps.game.utils import get_scoreboard_table_tag


class Command(BaseCommand):
    help = 'Creates a seeding league for the specified challenge.'

    def add_arguments(self, parser):
        parser.add_argument(
            'tag',
            type=str,
            help='tag to recognize the league'
        )
        parser.add_argument(
            'ref_tag',
            type=str,
            help='tag to previous league'
        )
        parser.add_argument(
            'test_team_pc_id',
            type=int,
            help='id of dummy team to complete groups.'
        )
        parser.add_argument(
            'group_size',
            type=int,
            help='id'
        )
        parser.add_argument(
            'challenge_id',
            type=int)
        parser.add_argument(
            'map_name',
            nargs='+',
            type=str)

    def handle(self, *args, **options):
        challenge_id = options['challenge_id']
        try:
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            raise CommandError('Challenge  "%s" does not exist.' % challenge_id)

        try:
            dummy_team = TeamParticipatesChallenge.objects.get(
                id=options['test_team_pc_id']).team
        except TeamParticipatesChallenge.DoesNotExist:
            raise CommandError('Dummy team "%s" does not exist.' % options['test_team_pc_id'])

        group_size = options['group_size']
        if group_size < 1:
            raise CommandError('group_size should be more than 0')

        teams_status = get_scoreboard_table_tag(options['ref_tag'])

        submitters = list(map(lambda x: x['team'], teams_status))
        submitters.remove(dummy_team)
        for submitter in submitters:
            print(submitter.name)

        n = submitters.__len__()
        submitters += [dummy_team for i in range((group_size - n % group_size) % group_size)]
        n = submitters.__len__()

        groups = [[] for i in range(n // group_size)]

        for i in range(n):
            groups[i % (groups.__len__())].append(submitters[i])

        for i in range(groups.__len__()):
            competition = Competition(
                tag=options['tag'],
                challenge=challenge,
                type='league',
                name='گروه %d لیگ اصلی انتخابی' % (i + 1)
            )
            competition.save()
            for m in Map.objects.filter(name__in=options['map_name']):
                competition.maps.add(m)
            competition.save()
            competition.create_new_league(groups[i], 1)
            competition.save()

        self.stdout.write(self.style.SUCCESS('Successfully created seeding league.'))
