from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
import os
from datetime import datetime
import gzip
import shutil

class Command(BaseCommand):
    help = 'Create a backup of the database and media files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output-dir',
            type=str,
            default='backups',
            help='Directory to store backups'
        )
        parser.add_argument(
            '--compress',
            action='store_true',
            help='Compress the backup files'
        )

    def handle(self, *args, **options):
        output_dir = options['output_dir']
        compress = options['compress']
        
        # Create backup directory
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Database backup
        db_backup_file = os.path.join(output_dir, f'db_backup_{timestamp}.json')
        
        self.stdout.write('📦 Creating database backup...')
        
        with open(db_backup_file, 'w') as f:
            call_command('dumpdata', stdout=f, indent=2)
        
        if compress:
            with open(db_backup_file, 'rb') as f_in:
                with gzip.open(f'{db_backup_file}.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            os.remove(db_backup_file)
            db_backup_file += '.gz'
        
        # Media files backup
        if hasattr(settings, 'MEDIA_ROOT') and os.path.exists(settings.MEDIA_ROOT):
            self.stdout.write('📁 Creating media files backup...')
            media_backup_file = os.path.join(output_dir, f'media_backup_{timestamp}')
            shutil.make_archive(media_backup_file, 'zip', settings.MEDIA_ROOT)
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Backup completed successfully!')
        )
        self.stdout.write(f'   Database: {db_backup_file}')
        if 'media_backup_file' in locals():
            self.stdout.write(f'   Media: {media_backup_file}.zip')