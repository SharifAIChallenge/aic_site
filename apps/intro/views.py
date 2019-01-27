import logging
from io import BytesIO

from PIL import Image
from django.contrib.auth.models import User
from django import forms
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import render

from apps.accounts.models import Team
from apps.game.models import TeamSubmission
from apps.intro.form import StaffForm
from apps.intro.models import Notification, Staff

logger = logging.getLogger(__name__)


def index(request):
    staff = Staff.objects.all().order_by('?')[0:5]
    print(staff.count())
    return render(request, 'intro/index.html', {
        'no_sidebar': False,
        'users_count': User.objects.count(),
        'submits_count': TeamSubmission.objects.count(),
        'teams_count': Team.objects.count(),
        'staff': staff,
    })


def faq(request):
    return render(request, 'intro/faq.html')


def not_found(request):
    logger.error("hello")
    logger.info("hello")
    logger.debug("hello")
    logger.warning("hello")
    return render(request, '404.html')

def notify(request):
    if request.POST:
        valid = True
        try:
            forms.EmailField().clean(request.POST['email'])
        except Exception as e:
            valid = False
        if valid:
            try:
                Notification.objects.create(email=request.POST['email'])
            except IntegrityError:
                return JsonResponse({'success': False})
            return JsonResponse({'success': True })
    return JsonResponse({'success': False})


def staffs(request):
    staff = Staff.objects.all()
    tech = ['site','graphic','game design','infrastructure','content','server and client']
    exe = ['executive','branding','design']
    head = ['head']
    return render(request, 'intro/staffs.html', {
        "staff": staff,
        "tech": tech,
        "exe": exe,
        "head": head,
    })

def add_staff(request):
    form = StaffForm(request.POST, request.FILES)
    if request.POST:
        if form.is_valid():
            image_field = form.cleaned_data['image']
            image_file = BytesIO(image_field.file.read())
            image = Image.open(image_file)
            h = image.size[1]
            w = image.size[0]
            if w < h:
                image = image.crop((0, (h - w) / 2, w, (h - w) / 2 + w)).resize((w, w), Image.ANTIALIAS)
            elif w > h:
                image = image.crop(((w - h) / 2, 0, (w - h) / 2 + h, h)).resize((h, h), Image.ANTIALIAS)
            image = image.resize((300, 300), Image.ANTIALIAS)
            image_file = BytesIO()
            image.save(image_file, 'PNG')
            image_field.file = image_file
            image_field.image = image
            Staff.objects.create(name=form.cleaned_data['name'], team=form.cleaned_data['team'], image=image_field)
    return render(request, 'intro/staff-form.html', {
        'form': form
    })
