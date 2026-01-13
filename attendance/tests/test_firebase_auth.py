from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from unittest.mock import patch

class FirebaseAuthTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('firebase_login')

    @patch('firebase_admin.auth.verify_id_token')
    def test_firebase_login_creates_user_and_lecturer(self, mock_verify):
        mock_verify.return_value = {
            'email': 'lecturer@example.com',
            'email_verified': True,
            'uid': 'uid123',
            'name': 'Test Lecturer'
        }
        res = self.client.post(self.url, data='{"idToken":"fake"}', content_type='application/json')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get('success'))
        user = User.objects.filter(username='lecturer@example.com').first()
        self.assertIsNotNone(user)
        self.assertTrue(hasattr(user, 'lecturer'))
