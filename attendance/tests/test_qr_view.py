from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from attendance.models import Unit, AttendanceSession, Lecturer
from attendance.qr_generator import generate_session_qr


class QRViewTests(TestCase):
    def setUp(self):
        # Create user, lecturer and unit
        user = User.objects.create_user(username='testlecturer', password='secret')
        self.lecturer = Lecturer.objects.create(user=user, staff_id='S001', department='Computer Science')
        self.unit = Unit.objects.create(code='CS101', name='Intro', lecturer=self.lecturer)

    def test_download_qr_serves_inline_and_attachment(self):
        # Create a session
        session = AttendanceSession.objects.create(
            unit=self.unit,
            lecturer=self.lecturer,
            date='2025-12-15',
            start_time='08:00',
            end_time='09:00',
            venue='Room 101'
        )

        # Generate QR and save to session
        qr_file = generate_session_qr(session, base_url='http://example.com')
        session.qr_code.save(qr_file.name, qr_file, save=True)

        url = reverse('download_qr', args=[str(session.id)])

        # Authenticate as the lecturer (view is login-protected)
        self.client.login(username='testlecturer', password='secret')

        # Inline view (default)
        resp_inline = self.client.get(url)
        self.assertEqual(resp_inline.status_code, 200)
        self.assertEqual(resp_inline['Content-Type'], 'image/png')
        self.assertIn('inline', resp_inline.get('Content-Disposition', ''))

        # Forced download
        resp_download = self.client.get(f'{url}?download=1')
        self.assertEqual(resp_download.status_code, 200)
        self.assertEqual(resp_download['Content-Type'], 'image/png')
        self.assertIn('attachment', resp_download.get('Content-Disposition', ''))
