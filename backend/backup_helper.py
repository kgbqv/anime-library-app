import os
import shutil
import logging
from datetime import datetime, timedelta

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, 'library.db')
BACKUP_DIR = os.path.join(BASE_DIR, 'backups')
LOG_PATH = os.path.join(BASE_DIR, 'backup.log')
RETENTION_DAYS = 7

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
)

def ensure_backup_dir():
    if not os.path.isdir(BACKUP_DIR):
        os.makedirs(BACKUP_DIR, exist_ok=True)
        logging.info(f"Created backup directory: {BACKUP_DIR}")

def make_backup():
    """Copy library.db to backups with a timestamped filename."""
    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    backup_filename = f"library_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    try:
        shutil.copy2(DB_PATH, backup_path)
        logging.info(f"Backup created: {backup_filename}")
    except Exception as e:
        logging.error(f"Failed to create backup: {e}")

def cleanup_old_backups():
    """Delete any backup file older than RETENTION_DAYS."""
    cutoff = datetime.utcnow() - timedelta(days=RETENTION_DAYS)
    for fname in os.listdir(BACKUP_DIR):
        if not fname.startswith('library_') or not fname.endswith('.db'):
            continue
        full_path = os.path.join(BACKUP_DIR, fname)
        # Extract timestamp from filename: library_YYYYMMDDTHHMMSSZ.db
        try:
            ts_str = fname[len('library_'):-len('.db')]
            file_time = datetime.strptime(ts_str, '%Y%m%dT%H%M%SZ')
        except ValueError:
            logging.warning(f"Skipping file with unexpected name: {fname}")
            continue
        if file_time < cutoff:
            try:
                os.remove(full_path)
                logging.info(f"Deleted old backup: {fname}")
            except Exception as e:
                logging.error(f"Failed to delete {fname}: {e}")

def backup():
    logging.info("Starting backup process")
    ensure_backup_dir()
    make_backup()
    cleanup_old_backups()
    logging.info("Backup process completed")
