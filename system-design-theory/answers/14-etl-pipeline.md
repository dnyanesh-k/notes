# Q14: Design an ETL Pipeline

---

## How to Approach This in an Interview

ETL is one of the most practical data engineering questions. Lead with the three phases (Extract, Transform, Load) but quickly show you understand the hard problems: handling incremental extraction efficiently, data quality failures in the middle of a pipeline, exactly-once semantics, and late-arriving data. The interesting discussion is usually CDC (Change Data Capture) vs polling, and when to use Spark vs dbt vs simple SQL.

---

## Clarifying Questions

**1. What are the sources?**

"Are we pulling from operational databases (MySQL, PostgreSQL), APIs (Salesforce, Stripe), files (S3, SFTP), or a mix?"

*Why this matters:* Databases can use CDC (real-time, efficient). APIs must be polled (rate-limited). Files need file detection (S3 event notifications). Each has different extraction patterns.

**2. Full load or incremental?**

"Is this a one-time historical backfill, daily full dump, or near-real-time incremental sync?"

*Why this matters:* Full load at 10GB/day is manageable. At 1TB/day, it's operationally expensive and may not meet SLA. Incremental extraction changes the data model requirements (every source table needs `updated_at` or CDC).

**3. What's the destination?**

"Analytics warehouse (Redshift, BigQuery, Snowflake), data lake (S3 + Athena), or operational store for another application?"

*Why this matters:* Analytics warehouses are columnar, optimized for reads. Write patterns differ (batch append vs upsert). Schema requirements differ.

**4. Data quality and SLAs?**

"What happens if 5% of records fail validation — skip and continue, or fail the entire run? How fresh must the data be (SLA)?"

*Why this matters:* Different business functions have different tolerances. Missing revenue transactions is critical. Missing marketing event logs is acceptable.

### Assumptions

```
- Sources: 5 operational PostgreSQL databases + 3 SaaS APIs (Salesforce, Stripe, Segment)
- Destination: Redshift (analytics warehouse) + S3 data lake (raw archive)
- Incremental extraction (CDC from databases, API polling from SaaS)
- Volume: 50M events/day, 500GB/day
- SLA: Operational data available in warehouse within 1 hour of being written to source
- Quality: < 0.1% validation failure rate, errors logged and reported, pipeline continues
```

---

## Back-of-Envelope Math

```
Volume: 500GB/day raw data
Processing: Transform + validate = 2x overhead → 1TB processing/day

Spark cluster for transformation:
  10 cores × 1GB/core/minute = 10GB/minute throughput
  500GB / 10GB/min = 50 minutes for daily batch
  Need to fit within 1-hour SLA window: OK with small buffer

S3 storage:
  Raw zone: 500GB/day × 365 days × 3 years = 547TB
  → S3 Intelligent Tiering: hot data (< 30 days) in S3 Standard, older in S3-IA
  → Cost: ~$0.023/GB Standard, ~$0.0125/GB Infrequent Access
  → ~$12K/year for raw zone

Redshift (analytics):
  Compressed columnar storage: 500GB raw → ~150GB in Redshift (3x compression typical)
  → 2 years: 150GB/day × 730 = 109TB Redshift storage
  → ra3.4xlarge: 128GB RAM, 32 vCPUs, managed storage $0.245/hr × 3 nodes = ~$5,400/month
```

---

## High Level Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          ETL PIPELINE ARCHITECTURE                          │
│                                                                              │
│  EXTRACT                                                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  Source Systems                                                        │ │
│  │                                                                        │ │
│  │  [PostgreSQL DBs] → Debezium CDC → Kafka topics (real-time)           │ │
│  │  [Salesforce API] → Polling Worker → Kafka topics (hourly)            │ │
│  │  [Stripe API]     → Webhook → Kafka topics (real-time)                │ │
│  │  [S3 file drops]  → S3 Event → Lambda → Kafka topics                  │ │
│  └─────────────────────────────────┬──────────────────────────────────────┘ │
│                                     │                                        │
│  RAW STORAGE (always land first)    │                                        │
│  ┌──────────────────────────────────▼──────────────────────────────────┐    │
│  │  S3 Raw Zone: s3://data-lake/raw/source=payments/date=2026-06-22/   │    │
│  │  Parquet files, partitioned by source + date. Never deleted.        │    │
│  │  This is the source of truth for replay if anything downstream fails│    │
│  └─────────────────────────────────┬───────────────────────────────────┘    │
│                                     │                                        │
│  TRANSFORM (Spark / dbt)            │                                        │
│  ┌──────────────────────────────────▼──────────────────────────────────┐    │
│  │  Staging:  Type casting, dedup, null checks, format normalization   │    │
│  │  Curated:  Business logic, joins, aggregations, SCD type 2          │    │
│  │            (dbt models run against Redshift staging tables)          │    │
│  └─────────────────────────────────┬───────────────────────────────────┘    │
│                                     │                                        │
│  LOAD (destination)                 │                                        │
│  ┌──────────────────────────────────▼──────────────────────────────────┐    │
│  │  Redshift:  Analytics warehouse (curated tables)                    │    │
│  │  S3 Curated Zone: Parquet, queryable via Athena                     │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ORCHESTRATION: Apache Airflow (DAGs, schedules, dependencies, retries)     │
│  MONITORING: Data quality checks, freshness alerts, row count validation    │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Part 1: Extraction — The Hard Part

### CDC vs Polling — What's the Difference?

**Polling (simple but expensive):**

```python
# Last extraction: 2026-06-22 09:00:00
# Current run: 2026-06-22 10:00:00

SELECT *
FROM orders
WHERE updated_at > '2026-06-22 09:00:00'
  AND updated_at <= '2026-06-22 10:00:00'
ORDER BY updated_at;
```

**Problems with polling:**
1. Requires every source table to have an `updated_at` column. Not all do.
2. If a record is deleted, polling misses it (there's no `updated_at` on a row that doesn't exist).
3. Reads every modified row — including unchanged columns. Expensive for wide tables.
4. If the source DB is under load, your polling query adds more load.

**CDC (Change Data Capture) — reading the DB transaction log:**

Every relational database writes every change (INSERT, UPDATE, DELETE) to a write-ahead log (WAL in PostgreSQL, binary log in MySQL). This log is how replication to read replicas works. CDC reads this log and publishes changes as events.

```
PostgreSQL WAL entry:
  timestamp: 2026-06-22T09:01:23.456Z
  transaction_id: 1234567
  operation: UPDATE
  table: orders
  before: { id: 42, status: "pending", updated_at: "..." }
  after:  { id: 42, status: "shipped", updated_at: "2026-06-22T09:01:23Z" }
```

**Why CDC is better:**
1. Zero load on source DB (reading the log, not querying tables)
2. Captures DELETEs
3. Captures every intermediate state (UPDATE then UPDATE again in 1 second — both captured)
4. Near-real-time (seconds of latency vs hour for hourly polling)

### Debezium: PostgreSQL CDC to Kafka

```yaml
# Debezium connector configuration (Kafka Connect)
name: postgres-orders-cdc
config:
  connector.class: io.debezium.connector.postgresql.PostgresConnector
  database.hostname: prod-postgres-01.internal
  database.port: 5432
  database.user: debezium_user   # read-only user with replication permission
  database.dbname: orders
  table.include.list: public.orders,public.order_items,public.payments
  
  # Kafka output
  topic.prefix: prod-cdc
  # Creates topics: prod-cdc.public.orders, prod-cdc.public.order_items
  
  # Snapshot: on first start, do a full table read to establish baseline
  snapshot.mode: initial
  
  # Use Avro schema registry for compact, schema-evolved messages
  key.converter: io.confluent.kafka.serializers.KafkaAvroSerializer
  value.converter: io.confluent.kafka.serializers.KafkaAvroSerializer
```

**What does each Kafka message look like?**

```json
{
  "op": "u",                 // u=update, c=create, d=delete, r=read(snapshot)
  "ts_ms": 1750582283456,    // timestamp from DB transaction log
  "source": {
    "db": "orders",
    "table": "orders",
    "lsn": 123456789         // log sequence number (position in WAL)
  },
  "before": {
    "id": 42,
    "status": "pending"
  },
  "after": {
    "id": 42,
    "status": "shipped",
    "shipped_at": "2026-06-22T09:01:23Z"
  }
}
```

The `lsn` (log sequence number) is the WAL position. Debezium checkpoints this in Kafka Connect's offset storage. If Debezium restarts, it resumes from the last `lsn` — no data is lost or duplicated.

### API Polling

```python
class SalesforceExtractor:
    """Polls Salesforce API for new/updated records since last run."""
    
    def __init__(self, client: SalesforceClient):
        self.client = client
        self.watermark_store = RedisWatermarkStore()
    
    def extract(self, object_name: str) -> list[dict]:
        # Load last successful extraction timestamp
        last_watermark = self.watermark_store.get(f"salesforce:{object_name}")
        
        if last_watermark is None:
            # First run: extract all (or past 90 days)
            last_watermark = datetime.now() - timedelta(days=90)
        
        # SOQL query with watermark filter
        query = f"""
            SELECT Id, Name, Amount, Stage, CreatedDate, LastModifiedDate
            FROM {object_name}
            WHERE LastModifiedDate > {last_watermark.isoformat()}
            ORDER BY LastModifiedDate ASC
            LIMIT 10000
        """
        
        records = []
        query_result = self.client.query(query)
        records.extend(query_result['records'])
        
        # Handle pagination (Salesforce returns up to 2000 per page)
        while 'nextRecordsUrl' in query_result:
            query_result = self.client.query_more(query_result['nextRecordsUrl'])
            records.extend(query_result['records'])
        
        if records:
            # Update watermark to latest record's modified date
            latest = max(r['LastModifiedDate'] for r in records)
            self.watermark_store.set(f"salesforce:{object_name}", latest)
        
        return records
```

**Watermark pitfall — late-arriving records:**

If a record is updated while our extraction is running (between `last_watermark` and `NOW()`), we might miss it. Standard fix: use a lookback window.

```python
# Instead of: WHERE LastModifiedDate > last_watermark
# Use:        WHERE LastModifiedDate > (last_watermark - 5 minutes)
# This re-extracts the last 5 minutes on every run
# Creates duplicates → must deduplicate in transformation stage
```

The 5-minute overlap ensures late-arriving records are caught. Deduplication on target handles the re-extracts.

---

## Part 2: Transformation

### Three-Zone Architecture

**Zone 1: Raw (S3)**

Exact copy of what was extracted. No transformation. Partitioned by source + date.

```
s3://data-lake/raw/
  source=debezium_orders/
    date=2026-06-22/
      hour=09/
        part-00001.parquet
        part-00002.parquet
```

**Why save raw first?**

If your transformation logic has a bug and corrupts data, the raw zone is your recovery point. Reprocess raw → staging → curated. Without raw zone, you'd need to re-extract from source — which may be slow, rate-limited, or no longer available (some APIs only return last 30 days).

**Zone 2: Staging (Redshift)**

Light transformations: type casting, deduplication, null checks, date parsing.

```sql
-- Staging table for orders
CREATE TABLE stg_orders (
    order_id        BIGINT       NOT NULL,
    customer_id     BIGINT       NOT NULL,
    status          VARCHAR(50)  NOT NULL,
    amount          DECIMAL(12,2),
    currency        CHAR(3)      NOT NULL DEFAULT 'USD',
    created_at      TIMESTAMP    NOT NULL,
    updated_at      TIMESTAMP    NOT NULL,
    
    -- ETL metadata
    _extracted_at   TIMESTAMP    NOT NULL,     -- when we extracted this
    _source         VARCHAR(100) NOT NULL,     -- 'debezium_orders' or 'salesforce'
    _row_hash       VARCHAR(64)  NOT NULL,     -- MD5 of all fields, for dedup
    
    PRIMARY KEY (order_id, _extracted_at)      -- allow dedup by row_hash in transformation
);
```

**Zone 3: Curated (Redshift / S3)**

Business logic, aggregations, Slowly Changing Dimensions (SCD). Built by dbt.

### dbt — SQL-First Transformation

```sql
-- models/curated/fct_orders.sql

-- This dbt model creates the fact_orders table in the analytics warehouse
-- It joins staging orders with staging customers and applies business logic

WITH deduped_orders AS (
    SELECT 
        order_id,
        customer_id,
        status,
        amount,
        currency,
        created_at,
        updated_at,
        
        -- Deduplicate: keep the latest version of each order
        ROW_NUMBER() OVER (
            PARTITION BY order_id 
            ORDER BY _extracted_at DESC
        ) AS rn
    FROM {{ ref('stg_orders') }}     -- dbt resolves to staging.stg_orders
),

latest_orders AS (
    SELECT * FROM deduped_orders WHERE rn = 1
),

enriched AS (
    SELECT
        o.order_id,
        o.customer_id,
        c.customer_name,
        c.customer_tier,                  -- 'enterprise', 'mid-market', 'smb'
        o.status,
        o.amount,
        o.currency,
        
        -- Convert all amounts to USD using daily exchange rates
        o.amount * ex.rate AS amount_usd,
        
        -- Categorize order size (business logic)
        CASE 
            WHEN o.amount_usd >= 10000 THEN 'large'
            WHEN o.amount_usd >= 1000  THEN 'medium'
            ELSE 'small'
        END AS order_size_bucket,
        
        o.created_at,
        o.updated_at,
        DATE_TRUNC('day', o.created_at) AS order_date  -- for partitioning
    FROM latest_orders o
    JOIN {{ ref('dim_customers') }} c ON o.customer_id = c.customer_id
    JOIN {{ ref('stg_exchange_rates') }} ex 
        ON ex.currency = o.currency 
        AND ex.date = DATE_TRUNC('day', o.created_at)
)

SELECT * FROM enriched
```

**Why dbt?**

dbt is SQL templating + testing + lineage for transformations. You write SQL, dbt handles:
- Dependencies: `{{ ref('stg_orders') }}` means "run stg_orders before this model"
- Testing: `not_null`, `unique`, `accepted_values` tests run after each model
- Lineage: auto-generates a DAG showing how tables depend on each other
- Documentation: auto-generates data catalog from SQL comments

### Slowly Changing Dimensions (SCD Type 2)

**The problem:** A customer changes their tier from 'smb' to 'enterprise' in June. Historical orders from January should still show 'smb' (the tier at order time). If you just update the customer record, you lose history.

**SCD Type 2 solution:** Never update. Insert a new row with `valid_from` / `valid_to` dates.

```sql
CREATE TABLE dim_customers (
    customer_sk     BIGINT PRIMARY KEY,    -- surrogate key (auto-increment)
    customer_id     BIGINT NOT NULL,       -- natural key from source system
    customer_name   VARCHAR(500),
    customer_tier   VARCHAR(50),
    
    -- Historical tracking
    valid_from      DATE NOT NULL,
    valid_to        DATE,                  -- NULL = current record
    is_current      BOOLEAN NOT NULL DEFAULT TRUE,
    
    INDEX idx_customer_id (customer_id),
    INDEX idx_current (customer_id, is_current)
);

-- When customer 42 changes tier from 'smb' to 'enterprise' on 2026-06-22:
-- 1. Close the old record:
UPDATE dim_customers SET valid_to = '2026-06-21', is_current = FALSE
WHERE customer_id = 42 AND is_current = TRUE;

-- 2. Insert new current record:
INSERT INTO dim_customers (customer_sk, customer_id, customer_name, customer_tier, valid_from)
VALUES (9999, 42, 'Acme Corp', 'enterprise', '2026-06-22');

-- Now query: "What was customer 42's tier when order was placed on 2026-01-15?"
SELECT c.customer_tier
FROM fct_orders o
JOIN dim_customers c ON o.customer_id = c.customer_id
    AND o.order_date BETWEEN c.valid_from AND COALESCE(c.valid_to, '9999-12-31')
WHERE o.order_id = 123;
-- Returns: 'smb' ✓ (historical accuracy preserved)
```

---

## Part 3: Orchestration with Airflow

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from datetime import datetime, timedelta

# DAG definition
dag = DAG(
    'daily_etl_pipeline',
    default_args={
        'owner': 'data-engineering',
        'retries': 3,
        'retry_delay': timedelta(minutes=5),
        'email_on_failure': True,
    },
    schedule_interval='0 */1 * * *',   # hourly
    start_date=datetime(2026, 6, 1),
    catchup=True,  # backfill missed runs (important for data pipelines)
)

# Tasks
extract_debezium_to_s3 = PythonOperator(
    task_id='extract_debezium_to_s3',
    python_callable=flush_kafka_to_s3,      # Kafka consumer: reads CDC events, writes Parquet to S3
    op_kwargs={'hour': '{{ ds_nodash }}{{ execution_date.hour }}'},
    dag=dag
)

validate_raw_data = PythonOperator(
    task_id='validate_raw_data',
    python_callable=run_data_quality_checks,
    dag=dag
)

load_to_staging = PythonOperator(
    task_id='load_to_staging',
    python_callable=copy_s3_to_redshift_staging,
    dag=dag
)

run_dbt_models = BashOperator(
    task_id='run_dbt_models',
    bash_command='cd /opt/dbt && dbt run --select staging.+ curated.+ --target prod',
    dag=dag
)

run_dbt_tests = BashOperator(
    task_id='run_dbt_tests',
    bash_command='cd /opt/dbt && dbt test --select staging.+ curated.+',
    dag=dag
)

notify_success = PythonOperator(
    task_id='notify_success',
    python_callable=send_pipeline_metrics_to_slack,
    dag=dag
)

# Dependency graph:
extract_debezium_to_s3 >> validate_raw_data >> load_to_staging >> run_dbt_models >> run_dbt_tests >> notify_success
```

**Airflow key concepts:**

- **DAG (Directed Acyclic Graph):** A pipeline defined as tasks + dependencies. "Extract before Transform before Load" = arrows in the DAG.
- **`catchup=True`:** If the pipeline was down for 6 hours, Airflow will run 6 backfill DAG runs automatically. Critical for data pipelines — you never want gaps in hourly data.
- **`retries=3`:** Each task automatically retries up to 3 times before failing. API calls can have transient failures; retries handle them.
- **Idempotency:** Each DAG run processes exactly the data for its `execution_date`. Running the same DAG run twice produces the same result (deduplication at staging handles re-runs).

---

## Part 4: Data Quality

```python
class DataQualityChecker:
    def run_checks(self, table: str, run_date: str) -> DataQualityReport:
        checks = [
            self.check_row_count(table, run_date),
            self.check_null_rates(table),
            self.check_value_ranges(table),
            self.check_referential_integrity(table),
            self.check_freshness(table),
        ]
        return DataQualityReport(table=table, checks=checks)
    
    def check_row_count(self, table: str, run_date: str) -> QualityCheck:
        """Row count must be within 10% of 7-day average."""
        today_count = db.scalar(f"SELECT COUNT(*) FROM {table} WHERE date = '{run_date}'")
        avg_7d = db.scalar(f"""
            SELECT AVG(daily_count) FROM (
                SELECT COUNT(*) AS daily_count 
                FROM {table} 
                WHERE date BETWEEN '{run_date}'::date - 7 AND '{run_date}'::date - 1
                GROUP BY date
            )
        """)
        
        if avg_7d == 0:
            return QualityCheck.PASS("no baseline yet")
        
        deviation = abs(today_count - avg_7d) / avg_7d
        
        if deviation > 0.5:
            return QualityCheck.FAIL(f"Row count deviation {deviation:.1%} > 50%")
        elif deviation > 0.1:
            return QualityCheck.WARN(f"Row count deviation {deviation:.1%} > 10%")
        return QualityCheck.PASS(f"{today_count} rows ({deviation:.1%} deviation)")
    
    def check_freshness(self, table: str) -> QualityCheck:
        """Latest record should be within 2 hours."""
        latest_ts = db.scalar(f"SELECT MAX(updated_at) FROM {table}")
        staleness = datetime.now() - latest_ts
        
        if staleness > timedelta(hours=2):
            return QualityCheck.FAIL(f"Data is {staleness} stale (SLA: 1 hour)")
        return QualityCheck.PASS(f"Latest data: {staleness} ago")
    
    def check_null_rates(self, table: str) -> list[QualityCheck]:
        """Critical columns must have < 1% nulls."""
        critical_columns = ['order_id', 'customer_id', 'amount', 'status', 'created_at']
        results = []
        
        for col in critical_columns:
            null_rate = db.scalar(f"""
                SELECT COUNT(*) FILTER (WHERE {col} IS NULL) * 1.0 / COUNT(*)
                FROM {table}
            """)
            
            if null_rate > 0.01:
                results.append(QualityCheck.FAIL(f"{col}: {null_rate:.1%} nulls > 1% threshold"))
            else:
                results.append(QualityCheck.PASS(f"{col}: {null_rate:.2%} nulls"))
        
        return results
```

**What happens on a quality failure?**

Strategy depends on severity:
- `WARN`: log alert to Slack/PagerDuty, but continue pipeline. Data is usable with caveats.
- `FAIL` on non-critical table: quarantine failing records to `error_zone/`, continue with clean records.
- `FAIL` on critical table (revenue, compliance): halt pipeline, page on-call engineer. Don't load corrupt data.

---

## Scale — What Breaks at 10x?

10x = 5TB/day, 500M events/day.

**Kafka throughput:**

Single Kafka broker: handles ~100MB/sec. At 5TB/day = 58MB/sec. Fine for 1 broker, but add replication (3 replicas = 3× writes). Use 3-5 brokers per 100MB/sec sustained throughput.

**Spark job duration:**

At 5TB/day with 10-core cluster: 5TB / 10GB/min = 500 minutes. Far exceeds 1-hour SLA.

Solution: Scale Spark cluster horizontally. With 100 cores (10 × 10-core workers): 50 minutes. Use Spark Structured Streaming instead of batch for sub-minute latency on critical tables.

**Redshift COPY performance:**

Redshift COPY from S3 scales with: (number of slices × 4MB blocks). An ra3.4xlarge has 24 slices. Optimal: split S3 files into at least 24 files per COPY command (one per slice). More files = faster parallel load.

**Late-arriving data:**

At 5TB/day, you have Spark jobs that may run for 50+ minutes. Data arriving in Kafka at T=0 might not land in S3 until T=50 for the same hourly batch.

Solution: Spark Structured Streaming with watermarks:

```python
from pyspark.sql import SparkSession
from pyspark.sql.functions import window

spark = SparkSession.builder.appName("StreamingETL").getOrCreate()

# Read from Kafka (Structured Streaming)
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "prod-cdc.public.orders") \
    .load()

# Parse and transform
parsed = df.selectExpr("CAST(value AS STRING)") \
    .select(from_json("value", order_schema).alias("data")) \
    .select("data.*")

# Watermark: accept late data up to 10 minutes late
# Data arriving more than 10 minutes late is dropped
windowed = parsed.withWatermark("updated_at", "10 minutes")

# Write to S3 every minute (micro-batch)
query = windowed.writeStream \
    .format("parquet") \
    .option("path", "s3://data-lake/raw/source=orders/") \
    .option("checkpointLocation", "s3://checkpoints/orders/") \
    .trigger(processingTime='1 minute') \
    .partitionBy("date", "hour") \
    .start()
```

---

## Trade-offs

**Spark vs dbt:**

Spark: processes data where it lives (S3, HDFS). Handles Python UDFs, complex ML feature engineering, files of any format. Heavyweight: cluster startup, JVM overhead. Best for: large-scale raw transformations, non-SQL logic.

dbt: SQL-only, runs against your warehouse (Redshift, BigQuery, Snowflake). Lightweight, fast iteration. Built-in testing and lineage. Best for: business logic SQL transformations against already-loaded warehouse tables.

**Recommended combination:** Spark for Extract+Load (raw → staging: file parsing, dedup, format conversion). dbt for Transform (staging → curated: business logic, joins, aggregations).

**ELT vs ETL:**

Traditional ETL: transform before loading (on-premises era — warehouses were expensive, compute was separate).

Modern ELT: extract → load raw → transform inside warehouse. Works because cloud warehouses (Redshift, BigQuery) have cheap storage and scalable compute. Load the raw data first (fast), then transform inside the warehouse using SQL (flexible, easy to debug). If transformation logic changes, re-run dbt models on already-loaded raw data. No re-extraction needed.

---

## Cross-Questions

**Q: How do you handle schema evolution? The source team adds a column.**

CDC approach: Debezium uses Confluent Schema Registry to version Avro schemas. When source adds a column:
1. New CDC events include the new field.
2. Old events don't have it (null in the new field).
3. Schema Registry enforces backward/forward compatibility.
4. Staging table: `ALTER TABLE stg_orders ADD COLUMN new_field VARCHAR(100);` — new records populate it, old records have NULL.
5. dbt model: `COALESCE(new_field, 'default_value')` handles nulls for historical records.

**Q: How do you implement exactly-once semantics in the pipeline?**

Exactly-once = each event is processed exactly once, even if the pipeline crashes mid-run.

End-to-end:
1. **Kafka → S3 (Spark Streaming):** Spark checkpoints track Kafka offsets. On restart, Spark resumes from the last checkpoint. Combined with S3 idempotent writes (same filename = overwrite), processing is exactly-once.

2. **S3 → Redshift (COPY):** Use `COPY ... FROM ... MANIFEST` with a unique manifest ID per run. If the COPY fails and retries, Redshift detects the manifest was already processed (by checking its metadata) and skips.

3. **dbt models:** All dbt models are idempotent. Running the same model twice produces the same result (INSERT OVERWRITE or MERGE). Idempotency is the key to retryable pipelines.

**Q: How do you backfill 2 years of historical data?**

Historical data in S3 raw zone: partition by `source + date`. Backfill = Spark job that processes specific date partitions.

```python
# Backfill: reprocess all data from 2024-01-01 to 2025-12-31
backfill_dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(730)]

# Launch one Spark job per month (parallelism without overwhelming Redshift)
for year_month in get_unique_months(backfill_dates):
    spark.read.parquet(f"s3://data-lake/raw/source=orders/date={year_month}*") \
         .transform(apply_staging_transformations) \
         .write.mode("overwrite") \
         .parquet(f"s3://data-lake/staging/orders/date={year_month}*")
```

Airflow manages this as a backfill run: `airflow dags backfill daily_etl_pipeline --start-date 2024-01-01 --end-date 2025-12-31`. With `catchup=True`, Airflow runs 730 DAG runs. Each processes one day's data. Parallelism controlled by `max_active_runs=10` — 10 days processed simultaneously.

**Q: How do you monitor pipeline health in production?**

4 key metrics:

1. **Data freshness:** `MAX(updated_at)` per table. Alert if > SLA (1 hour). Shows immediately if CDC is stuck.

2. **Row count deviation:** Today vs 7-day average. > 20% deviation = alert. Catches upstream incidents (source DB down = 0 rows).

3. **Processing lag:** Kafka consumer group lag (`kafka-consumer-groups --describe`). > 100K message lag = ingestion is falling behind. Scale Spark consumers.

4. **dbt test failure rate:** If dbt tests fail, tag the affected tables as `data_quality: degraded` in the data catalog. Dashboard users see a warning banner. They still get data but know it has quality issues.

All 4 metrics go to Datadog/Grafana. PagerDuty alerts on: freshness > 2h, row count deviation > 50%, processing lag > 500K, dbt test failure on critical table.
