"""
Database backup management command

Usage:
    python manage.py backup_db
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import shutil
from datetime import datetime
from pathlib import Path
from wetech.utils.logger import logger

class Command(BaseCommand):
    help = 'Backup SQLite database to backups directory'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--keep',
            type=int,
            default=30,
            help='Number of backups to keep (default: 30)',
        )
    
    def handle(self, *args, **options):
        keep_count = options['keep']
        
        # Get database path
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'Database file not found: {db_path}'))
            logger.error(f"Database backup failed: file not found at {db_path}")
            return
        
        # Create backups directory
        backup_dir = Path(settings.BASE_DIR) / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'db_backup_{timestamp}.sqlite3'
        backup_path = backup_dir / backup_filename
        
        try:
            # Copy database file
            shutil.copy2(db_path, backup_path)
            
            # Get file size
            file_size_mb = backup_path.stat().st_size / (1024 * 1024)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Backup created: {backup_filename} ({file_size_mb:.2f} MB)'
                )
            )
            logger.info(f"Database backup created: {backup_filename} ({file_size_mb:.2f} MB)")
            
            # Clean up old backups
            self._cleanup_old_backups(backup_dir, keep_count)
            
        except Exception as e:
            error_msg = f'Failed to create backup: {str(e)}'
            self.stdout.write(self.style.ERROR(error_msg))
            logger.error(f"Database backup failed: {str(e)}", exc_info=True)
    
    def _cleanup_old_backups(self, backup_dir, keep_count):
        """Remove old backups, keeping only the most recent ones"""
        try:
            # Get all backup files sorted by modification time (newest first)
            backups = sorted(
                backup_dir.glob('db_backup_*.sqlite3'),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            if len(backups) > keep_count:
                removed_count = 0
                for old_backup in backups[keep_count:]:
                    try:
                        old_backup.unlink()
                        removed_count += 1
                    except Exception as e:
                        logger.warning(f"Failed to remove old backup {old_backup}: {str(e)}")
                
                if removed_count > 0:
                    self.stdout.write(
                        self.style.WARNING(
                            f'Removed {removed_count} old backup(s)'
                        )
                    )
                    logger.info(f"Cleaned up {removed_count} old backup(s)")
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {str(e)}")

