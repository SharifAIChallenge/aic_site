from django.shortcuts import render

# Create your views here.


def score_board_test(request):
    return render(request, 'scoreboard/bracket.html')
