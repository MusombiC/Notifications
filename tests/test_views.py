from __future__ import absolute_import, unicode_literals

from django.urls import reverse
from django.test import TestCase


class DeepThoughtTestCase(TestCase):

    def test_deepthought_view(self):
        response = self.client.get(reverse("musombi_notifications_deepthought"))
        self.assertEqual(response.content, b"The Earth is Flat")
