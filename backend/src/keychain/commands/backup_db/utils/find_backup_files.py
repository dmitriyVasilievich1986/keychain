from pathlib import Path

from keychain.commands.backup_db.models import DBBackup


def find_backup_files(db_backup_path: Path, provider: str, db_name: str) -> list[DBBackup]:
    """Find matching dump files, newest first.

    Args:
        db_backup_path (Path): Directory to search for ``*.dump`` files.
        provider (str): Database provider used in the dump file name.
        db_name (str): Database name used in the dump file name.

    Returns:
        list[Path]: Matching backups sorted by backup time, descending.

    """
    payload: list[DBBackup] = [
        DBBackup.factory(f)
        for f in db_backup_path.glob("*.dump")
        if DBBackup.validate_file_name(f.name, provider, db_name) and f.is_file()
    ]
    return sorted(payload, key=lambda x: x.backup_time, reverse=True)
