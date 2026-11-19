import re
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from shared.config.config import get_logger

from shared.utils.backup_cos_utils import (
    list_backup_objects,
    split_cos_path,
)

logger = get_logger(__name__)

def calculate_retention_cutoff(
    reference_date: date,
    retention: int,
) -> date:
    """
    Calculate the oldest date to retain.
    Retention is expressed in calendar months.
    """

    if retention <= 0:
        raise ValueError(
            "Retention must be a positive integer"
        )

    return reference_date - relativedelta(
        months=retention
    )
    
def list_backup_partitions(
    client,
    bucket: str,
    table_prefix: str,
) -> dict:
    """
    List dated partitions under a backup table.
    Expected format: dat_comp=YYYYMMDD/
    """

    table_prefix = table_prefix.rstrip("/") + "/"

    paginator = client.get_paginator(
        "list_objects_v2"
    )

    partitions = {}

    for page in paginator.paginate(
        Bucket=bucket,
        Prefix=table_prefix,
        Delimiter="/",
    ):
        for item in page.get("CommonPrefixes", []):

            prefix = item["Prefix"]

            partition_name = (
                prefix[len(table_prefix):].rstrip("/")
            )

            match = re.fullmatch(
                r"dat_comp=(\d{8})",
                partition_name,
            )

            if not match:
                continue

            try:
                partition_date = datetime.strptime(
                    match.group(1),
                    "%Y%m%d",
                ).date()

            except ValueError:
                logger.warning(
                    "Invalid partition: %s", prefix
                )
                continue

            partitions[partition_date] = prefix

    return partitions
    
def delete_partition_objects(
    client,
    bucket: str,
    partition_prefix: str,
) -> int:
    """
    Delete all objects under a single partition.
    """

    if not re.search(
        r"/dat_comp=\d{8}/$",
        partition_prefix,
    ):
        raise ValueError(
            f"Invalid partition prefix: "
            f"{partition_prefix}"
        )

    objects = list_backup_objects(
        client,
        bucket,
        partition_prefix,
    )

    deleted_count = 0

    for i in range(0, len(objects), 1000):

        batch = objects[i:i + 1000]

        response = client.delete_objects(
            Bucket=bucket,
            Delete={
                "Objects": [
                    {"Key": obj["Key"]}
                    for obj in batch
                ],
                "Quiet": False,
            },
        )

        if response.get("Errors"):
            raise RuntimeError(
                f"COS deletion errors: "
                f"{response['Errors']}"
            )

        deleted_count += len(
            response.get("Deleted", [])
        )

    logger.info(
        "Deleted %s objects from %s",
        deleted_count,
        partition_prefix,
    )

    return deleted_count
    
def apply_backup_retention(
    client,
    paths,
    layer: str,
    table_name: str,
    reference_date: date,
    retention: int,
    dry_run: bool = True,
) -> dict:
    """
    Remove expired partitions from a backup table.
    """

    backup_layers = {
        "conformed": "bkp_conformed_layer",
        "reporting": "bkp_reporting_layer",
    }

    if layer not in backup_layers:
        raise ValueError(
            f"Unsupported backup layer: {layer}"
        )

    if not re.fullmatch(r"[A-Za-z0-9_]+", table_name):
        raise ValueError(
            f"Invalid table name: {table_name}"
        )

    backup_path = paths.data_layer_table_path(
        backup_layers[layer],
        table_name,
    )

    bucket, table_prefix = split_cos_path(
        backup_path
    )

    cutoff = calculate_retention_cutoff(
        reference_date,
        retention,
    )

    partitions = list_backup_partitions(
        client,
        bucket,
        table_prefix,
    )

    expired_partitions = {
        partition_date: prefix
        for partition_date, prefix in partitions.items()
        if partition_date < cutoff
    }

    deleted_objects = 0

    for partition_date, prefix in sorted(
        expired_partitions.items()
    ):
        logger.info(
            "Expired partition: %s | dry_run=%s",
            prefix,
            dry_run,
        )

        if not dry_run:
            deleted_objects += delete_partition_objects(
                client,
                bucket,
                prefix,
            )

    return {
        "table_name": table_name,
        "cutoff": cutoff.isoformat(),
        "expired_partitions": len(expired_partitions),
        "deleted_objects": deleted_objects,
        "dry_run": dry_run,
    }
