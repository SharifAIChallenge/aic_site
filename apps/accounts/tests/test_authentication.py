import os

from django.contrib.auth.models import User
from django.test import Client, TestCase


class TestAuthentication(TestCase):
    def setUp(self):
        super().setUp()
        os.environ['RECAPTCHA_TESTING'] = 'True'
        self.client = Client()

    def test_signup(self):
        self.assertEqual(
            self.client.get('/accounts/signup/').status_code,
            200
        )
        data = {
            'g-recaptcha-response': 'PASSED',
            'username': 'test_user',
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'email@test.com',
            'password1': 'test_password',
            'password2': 'test_password',
            'organization': 'Good Organization',
        }
        response = self.client.post('/accounts/signup/', data, follow=True)
        self.assertContains(response, '/accounts/login/', 2, 200)
        self.assertFalse(self.client.login(username='test_user', password='test_password'))
        user = User.objects.first()
        user.is_active = True
        user.save()
        self.assertTrue(self.client.login(username='test_user', password='test_password'))

    def tearDown(self):
        super().tearDown()
        os.environ['RECAPTCHA_TESTING'] = 'False'
