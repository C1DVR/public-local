
import logging
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def list_backup_objects(client, bucket, prefix):
    """List all objects below a COS prefix."""
    paginator = client.get_paginator("list_objects_v2")

    objects = []
    for page in paginator.paginate(
        Bucket=bucket,
        Prefix=prefix.rstrip("/") + "/"
    ):
        objects.extend(page.get("Contents", []))

    return objects


def copy_backup_objects(
    client,
    bucket,
    source_prefix,
    target_prefix,
):
    """Copy source objects to a backup prefix."""

    source_prefix = source_prefix.rstrip("/") + "/"
    target_prefix = target_prefix.rstrip("/") + "/"

    if source_prefix == target_prefix:
        raise ValueError("Source and target must differ")

    if target_prefix.startswith(source_prefix):
        raise ValueError("Target cannot be inside source")

    source_objects = list_backup_objects(
        client, bucket, source_prefix
    )

    if not source_objects:
        raise ValueError(
            f"No source objects found: {source_prefix}"
        )

    copied_count = 0
    copied_bytes = 0

    for obj in source_objects:
        source_key = obj["Key"]
        relative_key = source_key[len(source_prefix):]
        target_key = target_prefix + relative_key

        client.copy(
            {"Bucket": bucket, "Key": source_key},
            bucket,
            target_key,
        )

        target = client.head_object(
            Bucket=bucket,
            Key=target_key,
        )

        if target["ContentLength"] != obj["Size"]:
            raise ValueError(
                f"Size mismatch: {target_key}"
            )

        copied_count += 1
        copied_bytes += obj["Size"]

    logger.info(
        "Copied %s objects (%s bytes)",
        copied_count,
        copied_bytes,
    )

    return {
        "objects": copied_count,
        "bytes": copied_bytes,
    }





    
    