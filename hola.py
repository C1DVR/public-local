
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

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


logger = get_logger(__name__)

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def run_backup(layer: str, **context):
    """
    Execute due backups for one logical layer.
    Initially runs in simulation mode.
    """

    reference_date = context["logical_date"].date()

    logger.info(
        "Starting backup | layer=%s | date=%s",
        layer,
        reference_date,
    )

    configs = load_backup_config(
        csv_key=BACKUP_CONFIG_PATH,
    )

    due_backups = select_due_backups(
        configs=configs,
        reference_date=reference_date,
        layers=(layer,),
    )

    logger.info(
        "Selected %s backup tables for %s",
        len(due_backups),
        layer,
    )

    paths = PathBuilder(
        data_bucket=COS_DATA_BUCKET,
        tech_bucket=COS_TECH_BUCKET,
    )

    results = []

    for config in due_backups:
        logger.info(
            "Processing backup | table=%s | layer=%s",
            config.table_name,
            config.layer,
        )

        result = backup_table(
            paths=paths,
            layer=config.layer,
            table_name=config.table_name,
            reference_date=reference_date,
            dry_run=True,
        )

        results.append(result)

    logger.info(
        "Backup simulation completed | layer=%s | tables=%s",
        layer,
        len(results),
    )

    return results


def create_backup_dag(dag_id: str, layer: str):

    with DAG(
        dag_id=dag_id,
        default_args=DEFAULT_ARGS,
        description=f"Scheduled COS backup for {layer}",
        schedule=None,
        start_date=datetime(2026, 11, 1),
        catchup=False,
        max_active_runs=1,
        tags=["backup", "cos", layer],
    ) as dag:

        PythonOperator(
            task_id="run_backup",
            python_callable=run_backup,
            op_kwargs={"layer": layer},
        )

    return dag


backup_conformed = create_backup_dag(
    dag_id="backup_conformed",
    layer="conformed",
)

backup_reporting = create_backup_dag(
    dag_id="backup_reporting",
    layer="reporting",
)

        
        
