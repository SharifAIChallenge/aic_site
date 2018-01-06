from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views import generic
# Create your views here.
from apps.accounts.forms.forms import SignUpForm


class SignupView(generic.CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy('')
    template_name = 'accounts/signup.html'