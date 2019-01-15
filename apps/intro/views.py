import logging

from PIL import Image
from django.contrib.auth.models import User
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from apps.accounts.models import Team
from apps.game.models import TeamSubmission
from apps.intro.models import Staff

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'intro/index.html', {
        'no_sidebar': False,
        'users_count': User.objects.count(),
        'submits_count': TeamSubmission.objects.count(),
        'teams_count': Team.objects.count(),
    })


def faq(request):
    return render(request, 'intro/faq.html')


def not_found(request):
    logger.error("hello")
    logger.info("hello")
    logger.debug("hello")
    logger.warning("hello")
    return render(request, '404.html')


def staffs(request):
    staff = Staff.objects.all()
    if request.POST and str(request.POST.get('team')) != 'همه':
        staff = Staff.objects.filter(team=request.POST.get('team'))
    return render(request, 'intro/staffs.html', {
        "staff": staff
    })

def add_staff(request):
    if request.POST:
        name = request.POST.get('name')
        team = request.POST.get('team')
        pic = request.FILES['photo']
        handle_uploaded_file(pic, str(name) + '.jpg')
        Staff.objects.create(name=name, team=team)
    return render(request, 'intro/staff-form.html')


def handle_uploaded_file(file, filename):

    with open('apps/intro/static/staff_pic/' + filename, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    image = Image.open('apps/intro/static/staff_pic/' + filename)
    cropped_image = image.crop((0, 0, 100, 100))
    resized_image = cropped_image.resize((100, 100), Image.ANTIALIAS)
    resized_image.save('apps/intro/static/staff_pic/' + filename)