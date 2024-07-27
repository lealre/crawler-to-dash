#!/bin/bash
# mongo_backup.sh

source .env

# Create Backup Inside the Container
docker exec $CONTAINER_NAME mongodump --out $BACKUP_PATH

# Copy Backup from Container to Host
docker cp "$CONTAINER_NAME:$BACKUP_PATH" "$LOCAL_BACKUP_PATH"

# Remove the backup file from the container after copying
docker exec $CONTAINER_NAME rm -r $BACKUP_PATH
