
def build_backup_paths(
    paths,
    layer: str,
    table_name: str,
    reference_date,
) -> tuple[str, str]:
    """
    Build source and destination COS paths.

    Supported layers:
        conformed
        reporting

    Backup partition:
        dat_comp=YYYYMMDD
    """

    layer_mapping = {
        "conformed": (
            "conformed_layer",
            "bkp_conformed_layer",
        ),
        "reporting": (
            "reporting_layer",
            "bkp_reporting_layer",
        ),
    }

    if layer not in layer_mapping:
        raise ValueError(
            f"Unsupported backup layer: {layer}"
        )

    source_layer, backup_layer = layer_mapping[layer]

    source_path = paths.data_layer_table_path(
        source_layer,
        table_name,
    )

    backup_root = paths.data_layer_table_path(
        backup_layer,
        table_name,
    )

    partition = reference_date.strftime("%Y%m%d")

    target_path = (
        f"{backup_root.rstrip('/')}/"
        f"dat_comp={partition}/"
    )

    return source_path, target_path

