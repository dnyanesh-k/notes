# Q14: Design ETL Pipeline at Scale

---

## Clarifying Questions

A few things to clarify. What are the data sources — relational databases, flat files (CSV/JSON), event streams, or third-party APIs? Each source requires a different extraction strategy.

What's the transformation complexity — simple type casting and renaming, or complex business logic like joining multiple sources, computing aggregates, and applying ML models?

What's the loading target — a data warehouse (Redshift, BigQuery), a data lake (S3 + Parquet), or an operational database? The loading strategy differs.

Is this batch (run nightly) or streaming (near-real-time, process as events arrive)? Or both — a lambda architecture?

What's the data volume — gigabytes or petabytes per day? And what's the SLA for freshness — daily batch is fine, or must data be available within minutes?

*Assuming: multi-source ETL (PostgreSQL transactional DBs, CSV file drops from partners, REST APIs), complex transformations with joins, loading to a data warehouse (BigQuery/Redshift), both batch (nightly) and near-real-time (30-minute delay), 500GB/day.*

---

## Scope

I'll design: source connectors, incremental extraction, transformation layer with error handling, target loading strategy, pipeline orchestration, lineage tracking, and monitoring. I'll cover both batch and streaming paths.

---

## High Level Design

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ETL PIPELINE                                         │
│                                                                               │
│  SOURCES                EXTRACT                TRANSFORM            LOAD     │
│                                                                              │
│  PostgreSQL ──────────▶ CDC Connector ──┐                                   │
│  (transactional)        (Debezium)      │                                   │
│                                         │                                   │
│  CSV Files ───────────▶ File Watcher ───┤                                   │
│  (S3 partner drops)     (S3 events)     ├──▶ Kafka ──▶ Spark/dbt ──▶ DW   │
│                                         │   (staging)  (transform)          │
│  REST APIs ────────────▶ API Poller ────┘                                   │
│  (3rd party)            (cron-based)                                        │
│                                                                              │
│  ORCHESTRATION: Apache Airflow (DAG scheduling, dependency management)      │
│  MONITORING:    Lineage tracking, data quality checks, alerting             │
│  STORAGE:       S3 as raw data lake (immutable), DW as curated layer        │
└──────────────────────────────────────────────────────────────────────────────┘

Two paths:
  Batch path:  nightly full/incremental extract → S3 → Spark transform → DW
  Stream path: CDC events → Kafka → Spark Streaming → DW (upsert)
```

---

## Deep Dive 1 — Extraction Strategies

### CDC (Change Data Capture) from Relational DBs

**The wrong way:** `SELECT * FROM orders WHERE updated_at > last_run_time`. This is called "timestamp-based extraction." Problems: if `updated_at` isn't indexed or isn't set correctly, you miss rows. Hard deletes are invisible — a deleted row never shows `updated_at`. Doesn't capture what changed, only that something changed.

**The right way: CDC with Debezium.** Debezium reads the PostgreSQL Write-Ahead Log (WAL) — the same log PostgreSQL uses for replication. Every INSERT, UPDATE, DELETE produces a log entry. Debezium streams these as events to Kafka:

```json
{
  "before": { "id": 123, "status": "pending", "amount": 500 },
  "after":  { "id": 123, "status": "shipped", "amount": 500 },
  "op": "u",           // u = update, c = create, d = delete
  "ts_ms": 1687391823000,
  "source": { "table": "orders", "db": "production" }
}
```

CDC captures everything including deletes and gives you the before/after state. This is how production ETL is done for transactional databases.

**Setting up CDC on PostgreSQL:**
```sql
-- Enable logical replication
ALTER SYSTEM SET wal_level = logical;

-- Create a replication slot (Debezium uses this)
SELECT pg_create_logical_replication_slot('debezium_slot', 'pgoutput');

-- Create a publication for tables we want to capture
CREATE PUBLICATION debezium_pub FOR TABLE orders, customers, products;
```

### File-based Extraction (Partner CSV Drops)

Partners drop CSV files to S3 at regular intervals. S3 event notifications trigger SQS, which triggers an extraction Lambda:

```python
def handle_s3_event(event):
    s3_key = event['Records'][0]['s3']['object']['key']
    
    # Validate: schema, file format, expected columns
    df = pd.read_csv(s3.get_object(key=s3_key))
    
    if not validate_schema(df, expected_columns=['order_id', 'amount', 'date']):
        alert_ops(f"Schema mismatch in {s3_key}")
        return
    
    # Write to S3 raw zone (Parquet for efficiency)
    df.to_parquet(f"s3://raw-zone/{partner}/{date}/{filename}.parquet")
    
    # Publish extraction event to Kafka
    kafka_producer.send('raw_data_available', { 's3_key': parquet_path, 'source': partner })
```

### REST API Extraction

For third-party APIs that don't support CDC:

```python
class APIPoller:
    def __init__(self, api_config: APIConfig):
        self.last_cursor = self.load_cursor()  # last page token or timestamp
    
    def extract(self) -> list[dict]:
        records = []
        cursor = self.last_cursor
        
        while True:
            response = requests.get(
                self.api_config.endpoint,
                params={ 'since': cursor, 'limit': 1000 },
                headers={ 'Authorization': f'Bearer {self.api_config.token}' }
            )
            batch = response.json()['data']
            records.extend(batch)
            
            cursor = response.json().get('next_cursor')
            if not cursor or len(batch) == 0:
                break
        
        self.save_cursor(cursor)  # persist for next run
        return records
```

Key principle: always save the cursor/offset after successful extraction. This makes extraction idempotent — restart from the last successful position, never re-extract everything.

---

## Deep Dive 2 — Transformation with dbt and Spark

### Raw → Staging → Transformed (Three-layer Data Lake)

```
S3 Raw Zone (immutable — never modify)
    → exact copy of source data, partitioned by ingestion_date
    → Parquet format (columnar, compressed, fast to query)

S3 Staging Zone
    → cleaned and standardized (types, nulls, deduplication)
    → schema validated

S3 Curated Zone (or Data Warehouse)
    → business logic applied (joins, aggregations, derived fields)
    → ready for analysts and BI tools
```

**Why keep raw immutable?** If a transformation has a bug and corrupts data, you can always re-run the transformation from the raw zone. Without the raw zone, the original data is gone.

### dbt for SQL-based Transformations

dbt (data build tool) runs SQL transformations in the warehouse. Great for structured transformations with clear lineage:

```sql
-- models/staging/stg_orders.sql
SELECT
    id                                    AS order_id,
    customer_id,
    CAST(amount AS DECIMAL(10,2))         AS amount_usd,
    LOWER(status)                         AS status,
    DATE(created_at AT TIME ZONE 'UTC')   AS order_date,
    _ingested_at                          AS ingested_at
FROM {{ source('raw', 'orders') }}
WHERE id IS NOT NULL          -- filter out corrupt rows
  AND amount > 0              -- business rule: no zero/negative orders

-- models/marts/fct_orders.sql
SELECT
    o.order_id,
    o.order_date,
    o.amount_usd,
    c.customer_name,
    c.country,
    p.product_category
FROM {{ ref('stg_orders') }} o
JOIN {{ ref('stg_customers') }} c ON o.customer_id = c.customer_id
JOIN {{ ref('stg_order_items') }} oi ON o.order_id = oi.order_id
JOIN {{ ref('stg_products') }} p ON oi.product_id = p.product_id
```

dbt handles: dependency resolution (which model to run first), incremental updates (only process new rows, not full re-runs), testing (assert no NULLs in critical fields, assert referential integrity), and lineage documentation.

### Spark for Large-scale Transformations

For transformations that don't fit in SQL or need distributed computing:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, window

spark = SparkSession.builder.appName("ETL").getOrCreate()

# Read from S3 raw zone
orders_df = spark.read.parquet("s3://raw-zone/orders/2026-06-21/")
customers_df = spark.read.parquet("s3://raw-zone/customers/2026-06-21/")

# Join and aggregate
result = (orders_df
    .join(customers_df, "customer_id", "left")
    .filter(col("status") == "completed")
    .groupBy("customer_id", "customer_name", "country")
    .agg(
        sum("amount").alias("total_revenue"),
        count("order_id").alias("order_count")
    )
    .filter(col("total_revenue") > 0)
)

# Write to DW staging table
result.write.mode("overwrite").parquet("s3://curated/customer_revenue/2026-06-21/")
```

---

## Deep Dive 3 — Orchestration with Airflow

Apache Airflow manages the DAG (Directed Acyclic Graph) of pipeline tasks. Each node in the DAG is a task; edges define dependencies.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from datetime import datetime, timedelta

with DAG(
    dag_id='orders_etl',
    schedule_interval='0 2 * * *',          # run at 2AM daily
    start_date=datetime(2026, 1, 1),
    catchup=False,                           # don't backfill missed runs
    default_args={
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': alert_slack   # notify on failure
    }
) as dag:

    extract_orders = PythonOperator(
        task_id='extract_orders_from_postgres',
        python_callable=extract_orders_cdc
    )
    
    validate_raw = PythonOperator(
        task_id='validate_raw_data',
        python_callable=run_data_quality_checks
    )
    
    transform_staging = BigQueryInsertJobOperator(
        task_id='transform_to_staging',
        configuration={
            "query": {
                "query": "{{ dbt_run_model('stg_orders') }}",
                "useLegacySql": False,
            }
        }
    )
    
    load_to_mart = BigQueryInsertJobOperator(
        task_id='load_to_fact_table',
        configuration={"query": {"query": "{{ dbt_run_model('fct_orders') }}"}}
    )
    
    # DAG dependency chain
    extract_orders >> validate_raw >> transform_staging >> load_to_mart
```

---

## Deep Dive 4 — Data Quality Checks

Data quality failures are silent killers. A pipeline that runs successfully but produces wrong numbers is worse than a failed pipeline — at least failures are visible.

```python
class DataQualityCheck:
    def run_checks(self, df: DataFrame, table_name: str) -> QualityReport:
        results = []
        
        # Completeness: no nulls in critical fields
        null_counts = df.select([count(when(col(c).isNull(), c)).alias(c) 
                                 for c in ['order_id', 'customer_id', 'amount']])
        for field, null_count in null_counts.items():
            results.append(Check(f"{field}_not_null", null_count == 0, null_count))
        
        # Freshness: latest record not too old
        max_date = df.select(max("order_date")).first()[0]
        expected_min_date = datetime.now() - timedelta(hours=26)
        results.append(Check("freshness", max_date >= expected_min_date, max_date))
        
        # Volume: row count within expected range
        row_count = df.count()
        yesterday_count = self.load_yesterday_count(table_name)
        pct_change = abs(row_count - yesterday_count) / yesterday_count
        results.append(Check("volume_stable", pct_change < 0.2, pct_change))
        
        # Referential integrity: all customer_ids exist in customers table
        orphan_count = df.join(customers_df, "customer_id", "left_anti").count()
        results.append(Check("no_orphan_customers", orphan_count == 0, orphan_count))
        
        # Fail fast if critical checks fail
        critical_failures = [r for r in results if not r.passed and r.is_critical]
        if critical_failures:
            raise DataQualityException(critical_failures)
        
        return QualityReport(results)
```

If quality checks fail, the pipeline halts before loading bad data to the warehouse. Alert goes to the data team. This is the most important investment in ETL reliability.

---

## Scale — What Breaks at 10x?

At 5TB/day:

**Extraction bottleneck:** CDC with Debezium scales by partitioning Kafka topics by table. Multiple Debezium connectors for different source databases. Kafka handles petabytes — not a bottleneck.

**Transformation bottleneck:** Spark is designed for this — add more worker nodes in the Spark cluster. Autoscaling: EMR or Databricks auto-scales based on data volume. Partition Parquet files by date — `ORDER BY ingestion_date` queries skip irrelevant partitions (partition pruning). At 5TB/day, a 64-node Spark cluster processes it in 30 minutes.

**Data warehouse loading:** BigQuery and Redshift handle PB-scale. Use bulk loading (COPY command for Redshift, BigQuery Storage API) — never row-by-row inserts. Bulk loads are 100x faster.

**Airflow scaling:** Airflow's scheduler is a single process. For 1,000+ DAGs, use a CeleryExecutor (distribute task execution across workers) and separate the scheduler from the worker. For very high-scale (10K+ DAGs), consider migrating to Prefect or Dagster which have better multi-scheduler support.

---

## Trade-offs

**Batch vs streaming:** Batch (nightly) is simpler, cheaper, easier to debug, and handles full re-runs gracefully. Streaming (Kafka + Spark Streaming) gives near-real-time freshness but is operationally complex and more expensive. Use batch for analytical workloads where day-old data is fine. Add streaming only for specific use cases where freshness matters (fraud detection, real-time dashboards). Don't stream everything by default.

**ELT vs ETL:** Traditional ETL transforms before loading. Modern ELT loads raw data to the warehouse first, then transforms using SQL/dbt. ELT is preferred with cloud warehouses (BigQuery, Snowflake) because computation in the warehouse is cheap and SQL transformations are debuggable. ELT also preserves the raw data always. Use ETL (transform before load) only when the target warehouse is expensive or when data must be masked before landing.

**Full load vs incremental:** Full load re-processes all historical data on every run — simple but slow at scale. Incremental load processes only changed records — fast but requires careful tracking of what changed. Use incremental for tables > 1M rows where full reprocessing takes hours. dbt's `incremental` materialization handles this automatically with an `is_incremental()` check.

---

## Cross-Questions

**How do you handle schema changes in the source database — like a new column being added?**

The raw zone Parquet files automatically get the new column from the next extraction (Parquet is schema-flexible). The staging model needs updating to include the new column. Use dbt's schema testing: `dbt test` runs before any transformation — if the expected schema doesn't match the source, the test fails and the pipeline halts. To handle unknown columns gracefully: staging models use `SELECT *` from source but explicitly name output columns. New source columns are ignored until the staging model is updated. Breaking schema changes (renamed or dropped columns) need a migration plan: run old and new staging models in parallel, validate, then switch.

**How do you handle late-arriving data — a record from yesterday arriving today?**

Partition data by `event_date` (when the event happened), not `ingestion_date` (when we processed it). Late records update the `event_date` partition, not today's partition. This requires reprocessing yesterday's partition when late data arrives. Set an SLA: records arriving up to 48 hours late are handled. Records older than 48 hours are rejected with an alert. In BigQuery: use `MERGE` statements that update existing records by event_date. In Redshift: UPDATE + INSERT (upsert) to the correct date partition.

**How do you ensure the pipeline is idempotent — safe to re-run on failure?**

Every step must produce the same result if run multiple times. Extraction: track the last-processed cursor/offset in a state table. On re-run, start from the same cursor — don't re-process what was already processed. Transformation: dbt's `incremental` models use MERGE (upsert) by primary key — running twice produces the same result as running once. Loading: use COPY with `TRUNCATE + INSERT` (full replace) for batch loads, or upsert by primary key for incremental. Never use INSERT INTO without deduplication — it creates duplicate rows on re-run.

**How do you track data lineage — where does a number in a report come from?**

Data lineage tracks: which source tables feed which transformations, which transformations produce which tables, which reports read from which tables. dbt generates lineage graphs automatically from model references (`{{ ref('model') }}`). For column-level lineage (which source column maps to which output column), tools like OpenLineage or Marquez capture this at runtime. When a report shows a wrong number, lineage lets you trace backwards: "This revenue figure comes from fct_orders → stg_orders → raw.orders → PostgreSQL orders table, extracted at 2AM on June 21." Root cause is findable in minutes.

**How would you add a real-time fraud detection model into this pipeline?**

Two options based on latency requirement. Near-real-time (30-second delay): the CDC stream from the orders table flows through Kafka. A Spark Streaming job applies the fraud model to each transaction as it arrives. Flagged transactions are written to a `fraud_alerts` Kafka topic and simultaneously loaded to the DW. Fully real-time (< 1 second): the fraud model is served as a microservice. The order processing service calls the fraud API synchronously before confirming the order. The ETL pipeline is not in this path — it's the analytical record. The fraud model itself is trained on data from the ETL pipeline (batch training job), but inference happens outside the ETL.
