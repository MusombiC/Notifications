from __future__ import absolute_import, unicode_literals

from django.urls import reverse
from django.test import TestCase
from musombi_notifications import fcm

class FCM(TestCase):

    def test_send_notification(self):

        notify = fcm.FCM()
        response = notify.sendNotification('example','example title')
        self.assertIsInstance(response, str)
    
    def test_send_notification_to_all(self):
        
        notify = fcm.FCM()
        responses = notify.sendNotificationToAll('example title')
        self.assertIsInstance(responses, list)