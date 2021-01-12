import json
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from django.core import serializers
from django.shortcuts import render

from voting.serializers import MinimalVotingSerializer
from authentication.models import UserProfile

from base import mods

class IndexView(TemplateView):
    template_name = 'decide/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['user_styles'] = UserProfile.styles;
        return context

def helpvoiceassistant(request):
    return render(request,'helpvoiceassistant.html',)