from django.test import Client, TestCase


# Create your tests here
class TestAccessibility(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_intro_accessibility(self):
        self.assertContains(
            self.client.get('/'),
            '/accounts/login',
            None,
            200
        )
        self.assertContains(
            self.client.get('/'),
            '/accounts/signup',
            None,
            200
        )
