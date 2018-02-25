from random import shuffle

from django.core.management.base import BaseCommand, CommandError
from apps.game.models import Challenge, TeamParticipatesChallenge, Competition, Map


class Command(BaseCommand):
    help = 'Creates a seeding league for the specified challenge.'

    def add_arguments(self, parser):
        parser.add_argument(
            'tag',
            type=str,
            help='tag to recognize the league'
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
        print((challenge_id))
        try:
            challenge = Challenge.objects.get(id=challenge_id)
        except Challenge.DoesNotExist:
            raise CommandError('Challenge  "%s" does not exist.' % challenge_id)

        team_pcs = challenge.teams.all()

        try:
            dummy_team = TeamParticipatesChallenge.objects.get(
                id=options['test_team_pc_id'])
        except TeamParticipatesChallenge.DoesNotExist:
            raise CommandError('Dummy team "%s" does not exist.' % options['test_team_pc_id'])

        group_size = options['group_size']
        if group_size < 1:
            raise CommandError('group_size should be more than 0')

        submitters = []
        for team_pc in team_pcs:
            if team_pc.has_submitted():
                if team_pc != dummy_team:
                    submitters.append(team_pc.team)

        shuffle(submitters)

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
                name='گروه %d لیگ اولیه انتخابی' % i
            )
            competition.save()
            for map in Map.objects.filter(name__in=options['map_name']):
                competition.maps.add(map)
            competition.save()
            competition.create_new_league(groups[i], 1)

        self.stdout.write(self.style.SUCCESS('Successfully closed poll "%s".' % challenge_id))
