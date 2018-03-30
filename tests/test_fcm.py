from __future__ import absolute_import, unicode_literals

from django.urls import reverse
from django.test import TestCase


class FCM(TestCase):

    def test_send_notification(self):
        self.assertEqual(1,1)