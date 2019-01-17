import logging
from io import BytesIO

from PIL import Image
from django.contrib.auth.models import User
from django.shortcuts import render
from apps.accounts.models import Team
from apps.game.models import TeamSubmission
from apps.intro.form import StaffForm
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
    if request.POST and str(request.POST.get('team')) != 'all':
        staff = Staff.objects.filter(team=request.POST.get('team'))
    return render(request, 'intro/staffs.html', {
        "staff": staff
    })

def add_staff(request):
    form = StaffForm(request.POST, request.FILES)
    if request.POST:
        if form.is_valid():
            image_field = form.cleaned_data['image']
            image_file = BytesIO(image_field.file.read())
            image = Image.open(image_file)
            size = image.size[1]
            image = image.crop((0, 0, size, size)).resize((size, size), Image.ANTIALIAS)
            image_file = BytesIO()
            image.save(image_file, 'PNG')
            image_field.file = image_file
            image_field.image = image
            member = Staff.objects.create(name=form.cleaned_data['name'], team=form.cleaned_data['team'], image=image_field)
    return render(request, 'intro/staff-form.html', {
        'form':form
    })

