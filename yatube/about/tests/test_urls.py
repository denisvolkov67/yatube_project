from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_anonymous_exists_at_desired_location(self):
        """Страницы доступны анонимному пользователю"""
        address_status_code_names = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for address, status_code in address_status_code_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)
