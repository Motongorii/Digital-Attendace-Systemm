from django.core.management.base import BaseCommand, CommandError
from attendance.models import AttendanceSession
from attendance.qr_generator import generate_session_qr
from django.conf import settings


class Command(BaseCommand):
    help = 'Regenerate QR codes for attendance sessions. By default only creates missing QR images.'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force regeneration even if QR already exists')
        parser.add_argument('--limit', type=int, help='Limit number of sessions to process')

    def handle(self, *args, **options):
        force = options.get('force', False)
        limit = options.get('limit')

        qs = AttendanceSession.objects.all().order_by('-date')
        if not force:
            qs = qs.filter(qr_code__isnull=True)

        if limit:
            qs = qs[:limit]

        count = qs.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No sessions to process.'))
            return

        self.stdout.write(f'Processing {count} sessions...')
        processed = 0
        for session in qs:
            try:
                base_url = getattr(settings, 'SITE_BASE_URL', None) or 'https://{host}'.format(host=settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost')
                qr_file = generate_session_qr(session, base_url=base_url)
                session.qr_code.save(qr_file.name, qr_file, save=True)
                processed += 1
                self.stdout.write(self.style.SUCCESS(f'Generated QR for session {session.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed for {session.id}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Done. Processed {processed} sessions.'))
