from __future__ import absolute_import, unicode_literals

from django.shortcuts import render

# Create your views here.

from django.http import HttpResponse
from django.views.generic import View
from . import fcm


class DeepThoughtView(View):

    def get(self, request):
        fcmm = fcm.FCM()
        response = fcmm.sendNotificationToAll("Hello Chris","Wow",{
            "help": "s",
            "sas":"d"
        },dry_run=True)
        # fcmm.__create_or_get_topic__(["example"])
        # x = fcmm.__getTokenList__(["example","example"])
        # myString = ",".join(x)
        return HttpResponse("The Earth is Flat")