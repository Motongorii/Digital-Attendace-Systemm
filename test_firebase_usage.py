from attendance.firebase_service import get_firebase_service

fb = get_firebase_service()
print('is_connected:', fb.is_connected)

payload = {
    'lecturer_id': 'TEST_LECT_1',
    'lecturer_name': 'Test Lecturer',
    'unit_code': 'TEST101',
    'unit_name': 'Testing 101',
    'venue': 'Room 0',
}

try:
    res = fb.save_attendance('test-session-1', payload)
    print('save_attendance result:', res)
    diag = fb.diagnose()
    print('diagnose:', diag)
except Exception as e:
    import traceback
    traceback.print_exc()
    print('error:', e)
