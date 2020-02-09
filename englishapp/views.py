from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import FormView

from . forms import RegistrationForm

def home_page(request):
    return render(request, 'home.html')

class RegisterFormView(FormView):
    form_class = RegistrationForm
    success_url = 'accounts/login/'
    template_name = 'register.html'

    def form_valid(self, form):
        form.save()
        return super(RegisterFormView, self).form_valid(form)

    def form_invalid(self, form):
        return super(RegisterFormView, self).form_invalid(form)