from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from attendance.models import Lecturer, Unit
import datetime


class CreateSessionAjaxTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='lect2', password='pw')
        self.lecturer = Lecturer.objects.create(user=user, staff_id='S200', department='CS')
        self.unit = Unit.objects.create(code='CS300', name='DB', lecturer=self.lecturer)
        self.client.login(username='lect2', password='pw')

    def test_ajax_create_session_returns_json(self):
        url = reverse('create_session')
        data = {
            'unit': self.unit.id,
            'date': datetime.date.today().isoformat(),
            'start_time': '09:00',
            'end_time': '10:00',
            'venue': 'Rm A',
            'class_year': 'Year 1',
            'semester': 1,
            'session_number': 1,
        }
        resp = self.client.post(url, data, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(resp.status_code, 200)
        json = resp.json()
        self.assertTrue(json.get('success'))
        self.assertIn('session_id', json)
