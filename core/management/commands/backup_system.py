import os
import zipfile
from datetime import datetime
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.core.mail import EmailMessage

class Command(BaseCommand):
    help = 'Backups critical system data (JSON) and archives it.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--email',
            action='store_true',
            help='Send backup via email (requires EMAIL configuration)'
        )

    def handle(self, *args, **options):
        # 1. Setup Backup Directory
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"spb_backup_{timestamp}.json"
        filepath = os.path.join(backup_dir, filename)
        zip_filename = f"spb_backup_{timestamp}.zip"
        zip_filepath = os.path.join(backup_dir, zip_filename)

        # 2. Dump Data
        self.stdout.write(f"Dumping data to {filename}...")
        with open(filepath, 'w', encoding='utf-8') as f:
            call_command(
                'dumpdata',
                'users',
                'market',
                'core',
                'ads',
                'crew',
                exclude=['auth.permission', 'contenttypes'],
                indent=2,
                stdout=f
            )

        # 3. Zip it
        self.stdout.write(f"Zipping to {zip_filename}...")
        with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(filepath, arcname=filename)

        # Remove raw JSON to save space
        os.remove(filepath)

        # 4. Email (if requested and configured)
        if options['email']:
            if getattr(settings, 'EMAIL_HOST', None):
                self.stdout.write("Sending email...")
                try:
                    email = EmailMessage(
                        'SPB Expert Auto Backup',
                        f'Attached is the automatic backup for {timestamp}.',
                        settings.DEFAULT_FROM_EMAIL,
                        [admin[1] for admin in settings.ADMINS] if getattr(settings, 'ADMINS', None) else ['admin@barge-expert.com'],
                    )
                    email.attach_file(zip_filepath)
                    email.send()
                    self.stdout.write(self.style.SUCCESS("Email sent successfully."))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to send email: {e}"))
            else:
                self.stdout.write(self.style.WARNING("EMAIL_HOST not configured. Skipping email."))

        # 5. Cleanup old backups (Keep last 10)
        backups = sorted([f for f in os.listdir(backup_dir) if f.endswith('.zip')])
        if len(backups) > 10:
            for old_backup in backups[:-10]:
                os.remove(os.path.join(backup_dir, old_backup))
                self.stdout.write(f"Removed old backup: {old_backup}")

        self.stdout.write(self.style.SUCCESS(f"Backup completed: {zip_filepath}"))
