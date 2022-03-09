from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse


class AboutTest(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages(self):
        about_urls = [
            reverse('about:author_static_page'),
            reverse('about:tech_static_page')
        ]
        for address in about_urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)
