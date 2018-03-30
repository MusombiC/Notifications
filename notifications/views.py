from __future__ import absolute_import, unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.views.generic import View


class DeepThoughtView(View):

    def get(self, request):
        return HttpResponse("The Earth is Flat")