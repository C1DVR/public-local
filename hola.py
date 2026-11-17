
def get_due_backups(
    reference_date: date,
    csv_key: str,
) -> List[BackupConfig]:
    """
    Load configuration and select backups
    for the ETL reference date.
    """
    configs = load_backup_config(csv_key)

    return select_due_backups(
        configs=configs,
        reference_date=reference_date,
        layers=("conformed", "reporting"),
    )
