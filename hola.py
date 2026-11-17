
def load_backup_config(
    csv_key: str,
    cos_client=None,
    bucket: str = None,
) -> List[BackupConfig]:
    """
    Load and validate the backup configuration
    from the TECH COS bucket.

    csv_key is the object key relative to the bucket.
    """
    client = cos_client if cos_client is not None else cos_tech
    bucket_name = bucket if bucket is not None else COS_TECH_BUCKET

    response = client.get_object(
        Bucket=bucket_name,
        Key=csv_key,
    )

    content = response["Body"].read().decode("utf-8-sig")

    return parse_backup_csv(content)
