#!/bin/bash
# Automated daily backup script for Riley AI Assistant
# Run via cron: 0 2 * * * /path/to/backup.sh

set -e

PROJECT_DIR="/Users/mark.kaough/.gemini/antigravity/scratch/local-llm-agent"
BACKUP_DIR="$HOME/.gemini/antigravity/backups"
DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_NAME="riley-backup-$DATE"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
echo "🔄 Creating backup: $BACKUP_NAME"
cd "$PROJECT_DIR/.."
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    --exclude="local-llm-agent/venv" \
    --exclude="local-llm-agent/*.log" \
    --exclude="local-llm-agent/.git" \
    local-llm-agent/

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "riley-backup-*.tar.gz" -mtime +30 -delete

echo "✅ Backup complete: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
echo "📊 Backup size: $(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)"

# Log to file
echo "$(date): Backup created - $BACKUP_NAME.tar.gz" >> "$BACKUP_DIR/backup.log"
