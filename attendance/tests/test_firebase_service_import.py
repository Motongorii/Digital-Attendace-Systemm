from django.test import TestCase


class FirebaseServiceImportTest(TestCase):
    def test_module_exposes_firebase_service_singleton(self):
        """Ensure that `from attendance.firebase_service import firebase_service` works
        and exposes the expected attributes. This guards against regressions where the
        symbol is removed or renamed.
        """
        try:
            from attendance.firebase_service import firebase_service
        except Exception as e:
            self.fail(f"Could not import firebase_service: {e}")

        # Basic attributes sanity-check
        self.assertIsNotNone(firebase_service)
        self.assertTrue(hasattr(firebase_service, "is_connected"))
        self.assertTrue(hasattr(firebase_service, "db"))
