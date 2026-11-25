from datetime import datetime, timedelta
import os
import sys

from airflow import DAG
from airflow.operators.python import PythonOperator

_dags_dir = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

if _dags_dir not in sys.path:
    sys.path.insert(0, _dags_dir)

from shared.config.config import (
    COS_DATA_BUCKET,
    COS_TECH_BUCKET,
    BACKUP_CONFIG_PATH,
    get_logger,
)
from shared.utils.utils import PathBuilder
from shared.utils.backup_config_utils import (
    load_backup_config,
    select_due_backups,
)
from shared.utils.backup_service import backup_table