from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect


def home(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/calendar')
    else:
        return render(request, 'index.html', {})
