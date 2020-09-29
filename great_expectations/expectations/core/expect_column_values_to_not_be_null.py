from typing import Dict

import pandas as pd

from great_expectations.core.batch import Batch
from great_expectations.execution_engine import (
    PandasExecutionEngine,
    SparkDFExecutionEngine,
)
from great_expectations.execution_engine.sqlalchemy_execution_engine import (
    SqlAlchemyExecutionEngine,
)
from great_expectations.expectations.expectation import ColumnMapDatasetExpectation


class ExpectColumnValuesToNotBeNull(ColumnMapDatasetExpectation):
    map_metric = "column_values.nonnull"
    metric_dependencies = "column_values.nonnull.count"

    @PandasExecutionEngine.column_map_metric(
        metric_name=map_metric,
        metric_domain_keys=ColumnMapDatasetExpectation.domain_keys,
        metric_value_keys=tuple(),
        metric_dependencies=tuple(),
        filter_column_isnull=False,
    )
    def _pandas_nonnull_count(
        self,
        series: pd.Series,
        metrics: dict,
        metric_domain_kwargs: dict,
        metric_value_kwargs: dict,
        runtime_configuration: dict = None,
        filter_column_isnull: bool = True,
    ):
        return ~series.isnull()

    @SqlAlchemyExecutionEngine.column_map_metric(
        metric_name=map_metric,
        metric_domain_keys=ColumnMapDatasetExpectation.domain_keys,
        metric_value_keys=tuple(),
        metric_dependencies=tuple(),
        filter_column_isnull=False,
    )
    def _sqlalchemy_nonnull_map_metric(
        self,
        column,
        metrics: dict,
        metric_domain_kwargs: dict,
        metric_value_kwargs: dict,
        runtime_configuration: dict = None,
        filter_column_isnull: bool = True,
    ):
        import sqlalchemy as sa

        return sa.not_(column.is_(None))

    @SparkDFExecutionEngine.column_map_metric(
        metric_name=map_metric,
        metric_domain_keys=ColumnMapDatasetExpectation.domain_keys,
        metric_value_keys=tuple(),
        metric_dependencies=tuple(),
    )
    def _spark_null_map_metric(
        self,
        data: "pyspark.sql.DataFrame",
        column: str,
        metrics: dict,
        metric_domain_kwargs: dict,
        metric_value_kwargs: dict,
        runtime_configuration: dict = None,
        filter_column_isnull: bool = True,
    ):
        import pyspark.sql.functions as F

        return data.withColumn(column + "__success", F.col(column).isNotNull())