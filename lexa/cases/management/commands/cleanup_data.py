from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from notifications.models import Notification
from client_portal.models import ClientAccess
from documents.models import DocumentShare

class Command(BaseCommand):
    help = 'Clean up old and expired data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Number of days to keep old notifications'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'🧹 Cleaning up data older than {days} days...')
        if dry_run:
            self.stdout.write('📋 DRY RUN - No data will be deleted')
        
        # Clean up old read notifications
        old_notifications = Notification.objects.filter(
            is_read=True,
            created_at__lt=cutoff_date
        )
        
        if dry_run:
            self.stdout.write(f'   Would delete {old_notifications.count()} old notifications')
        else:
            deleted_count = old_notifications.delete()[0]
            self.stdout.write(f'   Deleted {deleted_count} old notifications')
        
        # Clean up expired client access tokens
        expired_access = ClientAccess.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
        
        if dry_run:
            self.stdout.write(f'   Would deactivate {expired_access.count()} expired client access tokens')
        else:
            updated_count = expired_access.update(is_active=False)
            self.stdout.write(f'   Deactivated {updated_count} expired client access tokens')
        
        # Clean up expired document shares
        expired_shares = DocumentShare.objects.filter(
            expires_at__lt=timezone.now(),
            is_active=True
        )
        
        if dry_run:
            self.stdout.write(f'   Would deactivate {expired_shares.count()} expired document shares')
        else:
            updated_count = expired_shares.update(is_active=False)
            self.stdout.write(f'   Deactivated {updated_count} expired document shares')
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('✅ Cleanup completed successfully!')
            )