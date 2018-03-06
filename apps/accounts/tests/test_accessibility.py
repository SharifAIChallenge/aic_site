from django.test import Client, TestCase


class TestAccessibility(TestCase):
    def setUp(self):
        super().setUp()
        self.client = Client()

    def test_accounts_accessibility(self):
        response = self.client.get('/')
        self.assertContains(response, '/accounts/login', None, 200)
        self.assertContains(response, '/accounts/signup', None, 200)
        self.assertEqual(
            self.client.get('/accounts/login/').status_code,
            200
        )
        self.assertEqual(
            self.client.get('/accounts/signup/').status_code,
            200
        )
        self.assertEqual(
            self.client.get('/accounts/update_profile/').status_code,
            302
        )