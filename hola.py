
import csv
import io
from dataclasses import dataclass
from datetime import date
from typing import List


SUPPORTED_LAYERS = {
    "conformed",
    "reporting",
    "defaultbox",
}

REQUIRED_COLUMNS = {
    "table_name",
    "layer",
    "periodicity",
    "is_disabled",
    "retention",
}


@dataclass(frozen=True)
class BackupConfig:
    table_name: str
    layer: str
    periodicity: str
    is_disabled: bool
    retention: int


def parse_backup_csv(content: str) -> List[BackupConfig]:
    """
    Parse and validate the backup configuration CSV.
    Validation fails before any backup operation starts.
    """
    reader = csv.DictReader(io.StringIO(content))

    if not reader.fieldnames:
        raise ValueError("Backup CSV is empty")

    if set(reader.fieldnames) != REQUIRED_COLUMNS:
        raise ValueError(
            f"Invalid CSV columns: {reader.fieldnames}"
        )

    configs = []
    seen = set()

    for line_number, row in enumerate(reader, start=2):
        if None in row or any(
            value is None for value in row.values()
        ):
            raise ValueError(
                f"Malformed CSV row at line {line_number}"
            )

        row = {
            key: value.strip()
            for key, value in row.items()
        }

        table_name = row["table_name"]
        layer = row["layer"]
        periodicity = row["periodicity"]

        if not table_name:
            raise ValueError(
                f"Empty table_name at line {line_number}"
            )

        if layer not in SUPPORTED_LAYERS:
            raise ValueError(
                f"Unsupported layer '{layer}' "
                f"at line {line_number}"
            )

        if (
            not periodicity
            or any(c not in "1234567" for c in periodicity)
        ):
            raise ValueError(
                f"Invalid periodicity at line {line_number}"
            )

        disabled_value = row["is_disabled"].lower()

        if disabled_value not in ("true", "false"):
            raise ValueError(
                f"Invalid is_disabled at line {line_number}"
            )

        try:
            retention = int(row["retention"])
        except ValueError:
            raise ValueError(
                f"Invalid retention at line {line_number}"
            )

        if retention <= 0:
            raise ValueError(
                f"Retention must be positive "
                f"at line {line_number}"
            )

        key = (layer, table_name)

        if key in seen:
            raise ValueError(
                f"Duplicate backup configuration: {key}"
            )

        seen.add(key)

        configs.append(
            BackupConfig(
                table_name=table_name,
                layer=layer,
                periodicity=periodicity,
                is_disabled=disabled_value == "true",
                retention=retention,
            )
        )

    return configs


def is_backup_due(
    config: BackupConfig,
    reference_date: date,
) -> bool:
    """
    Check whether a weekly backup is due.
    Monday=1, Sunday=7.
    """
    if config.is_disabled:
        return False

    weekday = str(reference_date.isoweekday())

    return weekday in config.periodicity


def select_due_backups(
    configs: List[BackupConfig],
    reference_date: date,
    layers=("conformed", "reporting"),
) -> List[BackupConfig]:
    """
    Select eligible backup tables for a DAG run.
    """
    return [
        config
        for config in configs
        if config.layer in layers
        and is_backup_due(config, reference_date)
    ]
