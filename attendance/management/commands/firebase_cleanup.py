from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import json
import time
from pathlib import Path

from attendance.firebase_service import get_firebase_service


class Command(BaseCommand):
    help = 'Backup and optionally delete attendance data from Firebase. Use --dry-run to only preview, --session-id to target a session, --all to delete everything, and --confirm to actually delete.'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Do not delete; only backup and report')
        parser.add_argument('--session-id', type=str, help='Only target a specific session id')
        parser.add_argument('--all', action='store_true', help='Target all sessions and attendance_records')
        parser.add_argument('--confirm', action='store_true', help='Confirm deletion')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        session_id = options.get('session_id')
        delete_all = options.get('all')
        confirm = options.get('confirm')

        fb = get_firebase_service()
        if not fb.is_connected:
            raise CommandError('Firebase is not connected from this environment.')

        out = {}
        timestamp = int(time.time())
        out_path = Path(settings.BASE_DIR) / f'firebase_backup_{timestamp}.json'

        # Backup sessions -> students
        collections = {}

        if delete_all:
            # iterate all documents under 'sessions' and 'attendance_records'
            try:
                sessions = fb.db.collection('sessions').stream()
                collections['sessions'] = {}
                for doc in sessions:
                    doc_id = doc.id
                    data = doc.to_dict()
                    # dump children students
                    students = fb.db.collection('sessions').document(doc_id).collection('students').stream()
                    collections['sessions'][doc_id] = {'meta': data, 'students': {}}
                    for s in students:
                        collections['sessions'][doc_id]['students'][s.id] = s.to_dict()
                # attendance_records top-level collection
                ar_docs = fb.db.collection('attendance_records').stream()
                collections['attendance_records'] = {d.id: d.to_dict() for d in ar_docs}
            except Exception as e:
                raise CommandError(f'Error reading Firebase data: {e}')

        elif session_id:
            try:
                doc = fb.db.collection('sessions').document(session_id).get()
                if not doc.exists:
                    self.stdout.write(self.style.WARNING(f'Session {session_id} not found in Firebase.'))
                collections['sessions'] = {session_id: {'meta': doc.to_dict(), 'students': {}}}
                students = fb.db.collection('sessions').document(session_id).collection('students').stream()
                for s in students:
                    collections['sessions'][session_id]['students'][s.id] = s.to_dict()
            except Exception as e:
                raise CommandError(f'Error reading session data: {e}')
        else:
            raise CommandError('Specify --session-id or --all')

        # write backup
        out_path.write_text(json.dumps(collections, indent=2, default=str))
        self.stdout.write(self.style.SUCCESS(f'Backup written to {out_path}'))

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run - no deletion performed.'))
            return

        if not confirm:
            self.stdout.write(self.style.WARNING('Deletion not confirmed. Rerun with --confirm to delete.'))
            return

        # proceed with deletion
        deleted = {'sessions': [], 'attendance_records': []}
        try:
            if delete_all:
                # delete students subcollections then session docs
                for sess_id in collections.get('sessions', {}):
                    students = fb.db.collection('sessions').document(sess_id).collection('students').stream()
                    for s in students:
                        fb.db.collection('sessions').document(sess_id).collection('students').document(s.id).delete()
                    fb.db.collection('sessions').document(sess_id).delete()
                    deleted['sessions'].append(sess_id)
                for ar_id in collections.get('attendance_records', {}):
                    fb.db.collection('attendance_records').document(ar_id).delete()
                    deleted['attendance_records'].append(ar_id)
            else:
                # session_id deletion
                for sess_id in collections.get('sessions', {}):
                    students = fb.db.collection('sessions').document(sess_id).collection('students').stream()
                    for s in students:
                        fb.db.collection('sessions').document(sess_id).collection('students').document(s.id).delete()
                    fb.db.collection('sessions').document(sess_id).delete()
                    deleted['sessions'].append(sess_id)
        except Exception as e:
            raise CommandError(f'Error deleting data: {e}')

        self.stdout.write(self.style.SUCCESS(f'Deletion complete. Deleted: {deleted}'))
