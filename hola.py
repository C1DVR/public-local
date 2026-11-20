from datetime import date

from shared.config.config import (
    cos_data,
    COS_DATA_BUCKET,
    COS_TECH_BUCKET,
    BACKUP_CONFIG_PATH,
    get_logger,
)

from shared.utils.utils import PathBuilder

from shared.utils.backup_config_utils import (
    load_backup_config,
    is_backup_due,
)

from shared.utils.backup_cos_utils import (
    build_backup_paths,
    split_cos_path,
    list_backup_objects,
    copy_backup_objects,
)

from shared.utils.backup_retention_utils import (
    apply_backup_retention,
)

logger = get_logger(__name__)

def backup_table(
    paths: PathBuilder,
    layer: str,
    table_name: str,
    reference_date: date,
    dry_run: bool = True,
) -> dict:
    """
    Prepare and execute a backup for a single table.
    """

    source_path, target_path = build_backup_paths(
        paths=paths,
        layer=layer,
        table_name=table_name,
        reference_date=reference_date,
    )

    source_bucket, source_prefix = split_cos_path(
        source_path
    )

    target_bucket, target_prefix = split_cos_path(
        target_path
    )

    if source_bucket != target_bucket:
        raise ValueError(
            "Cross-bucket backups are not supported"
        )

    logger.info(
        "Backup table: %s | layer: %s | dry_run: %s",
        table_name,
        layer,
        dry_run,
    )

    logger.info("Source: %s", source_path)
    logger.info("Target: %s", target_path)

    objects = list_backup_objects(
        cos_data,
        source_bucket,
        source_prefix,
    )

    if not objects:
        raise ValueError(
            f"No source objects found: {source_path}"
        )

    result = {
        "table_name": table_name,
        "layer": layer,
        "source": source_path,
        "target": target_path,
        "objects": len(objects),
        "bytes": sum(obj["Size"] for obj in objects),
        "dry_run": dry_run,
    }

    if not dry_run:
        raise NotImplementedError(
            "Snapshot consistency must be validated "
            "before enabling backup writes"
        )

    return result

        
        
