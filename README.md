# crawler-to-dash

## MongoDB local Backup

The script [mongo_backup.sh](mongo_backup.sh) dumps the database to local storage in a file format. It uses the paths and container name specified in `.env` file.

The script first dumps the database content to a file inside the container, and it then copies the dump file from the container to the local storage.

Make the script executable:
```bash
chmod +x mongo_backup.sh
```

Execute the backup script:
```bash
./mongo_backup.sh
```

The `.env` file should contain the following variables:
```
CONTAINER_NAME="container-name"
BACKUP_PATH="/path/in/container"
LOCAL_BACKUP_PATH="/local/path/to/export"
```