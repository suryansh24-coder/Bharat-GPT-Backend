#!/bin/bash
set -e

# Load environment variables
DB_CONTAINER="bharatgpt_db"
DB_USER="postgres"
DB_NAME="bharatgpt"
BACKUP_DIR="/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql.gz"

echo "Starting automated database backup: $BACKUP_FILE"

# Run pg_dump inside the docker container
docker exec $DB_CONTAINER pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_FILE

echo "Backup successful! Retaining last 7 days..."

# Retention policy: Keep exactly 7 last backups, remove older
find $BACKUP_DIR -name "*.sql.gz" -type f -mtime +7 -delete

echo "Retention policy executed."
