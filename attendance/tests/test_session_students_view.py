from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from attendance.models import Lecturer, Unit, AttendanceSession, Student, Attendance
import datetime


class SessionStudentsViewTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='lect1', password='pw')
        self.lecturer = Lecturer.objects.create(user=user, staff_id='S100', department='CS')
        self.unit = Unit.objects.create(code='CS200', name='Algo', lecturer=self.lecturer)
        self.session = AttendanceSession.objects.create(
            unit=self.unit,
            lecturer=self.lecturer,
            date=datetime.date.today(),
            start_time='10:00',
            end_time='11:00',
            venue='Room 3'
        )
        # Enroll students
        self.s1 = Student.objects.create(admission_number='ADM001', name='Alice')
        self.s2 = Student.objects.create(admission_number='ADM002', name='Bob')
        self.s1.units.add(self.unit)
        self.s2.units.add(self.unit)

    def test_enrolled_students_list_shown_and_present_marked(self):
        # Mark Alice as present
        Attendance.objects.create(student=self.s1, session=self.session)

        self.client.login(username='lect1', password='pw')
        url = reverse('session_detail', args=[str(self.session.id)])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        content = resp.content.decode('utf-8')
        # Both students should be in the page
        self.assertIn('Alice', content)
        self.assertIn('Bob', content)
        # Alice should be marked Present (badge)
        self.assertIn('badge-success', content)
