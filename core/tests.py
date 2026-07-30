from django.test import TestCase
from django.urls import reverse

class MCSCBasicTests(TestCase):
    def test_home_page_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_about_page_status_code(self):
        url = reverse('about')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_grievances_portal_redirects_for_anonymous(self):
        url = reverse('grievance_portal')
        response = self.client.get(url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
