from attendance.firebase_service import get_firebase_service

fb = get_firebase_service()
print('is_connected', fb.is_connected)
try:
    col = fb.db.collection('lecturer_usage')
    docs = list(col.limit(5).stream())
    print('lecturer_usage doc count', len(docs))
    for d in docs:
        print('lecturer id', d.id, d.to_dict())

    # Example: record a test usage (will only run if connected)
    test_payload = {
        'lecturer_id': 'TEST_LECT_1',
        'lecturer_name': 'Test Lecturer',
        'unit_code': 'TEST101',
        'unit_name': 'Testing 101',
        'venue': 'Room 0',
    }
    res = fb.save_attendance('test-session-1', test_payload)
    print('save_attendance result:', res)

    # Read back the test lecturer doc
    doc = col.document('TEST_LECT_1').get()
    if doc.exists:
        print('test lecturer doc:', doc.to_dict())
    else:
        print('test lecturer doc not found (expected if offline)')

except Exception as e:
    import traceback
    traceback.print_exc()
    print('error', e)