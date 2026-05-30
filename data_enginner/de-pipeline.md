# Data Engineering Pipeline — End-to-End Deep Dive
### Inbound → Bronze → Silver | Interview & Understanding Reference

> **Audience**: DE with 5 YOE preparing for technical depth and system-design interviews.  
> **Scope**: Inbound files through to the Silver enriched layer. Generic and technical — no customer-specific names or internal paths.

---

## Mental Model First

Before going layer by layer, hold this one mental model:

> Raw data arrives as files. Those files are picked up, standardized, and loaded into a **staging store**. From there, a **transformation engine** reshapes the data into domain entities. Those entities are **enriched** (term-mapped, deduped, soft-deleted) and written to the final **Silver layer**, which is the source of truth for all downstream consumers.

Each layer exists because the layer before it isn't clean enough for the next operation. That's the core reason for medallion-style architectures.

---

## Layer 0 — Source Systems and Delivery

### What Happens

Data originates from external systems — EHR platforms, payers, claims clearinghouses, lab systems. These systems push files on their own schedules. The delivery mechanism is almost always one of three things:

- **SFTP**: The most common. The source drops a file to an SFTP endpoint. The platform has an agent that mirrors those files to cloud object storage (S3) on a continuous or scheduled basis.
- **HL7 / ADT feeds**: Near-real-time event streams. A hospital fires an HL7 message every time a patient is admitted, discharged, or transferred. These arrive as a continuous stream, not a batch drop.
- **API pulls**: Some payers expose APIs (FHIR, proprietary REST). A scheduled job calls the API and writes the response to object storage.

### Key Technical Points

- Files land in a **dedicated inbound prefix** in object storage, organized by customer and source.
- The SFTP mirror step is separate from ingestion — it purely syncs bytes, no parsing.
- A **state tracking mechanism** (zero-byte marker files) prevents the same file from being processed twice. Without this, every connector restart would reprocess the entire backlog.
- File formats vary enormously: CSV (pipe-delimited, comma-delimited, fixed-width), EDI/X12 (claims), HL7 v2 (clinical events), CDA/CCDA XML (clinical documents), Avro (EHR agent output), Excel, custom tab-delimited.
- File sizes range from a few KB to multi-GB bulk historical loads.

### Interview Angle

*"How do you handle idempotency at ingestion?"* — The state file pattern is the answer. Once a file is marked as processed (zero-byte marker written), the connector skips it on subsequent runs. This gives you exactly-once semantics at the file boundary without needing transactional infrastructure.

---

## Layer 1 — Event-Driven Triggering

### What Happens

Rather than each connector polling storage constantly, a centralized **event service** watches for file arrival notifications and triggers the appropriate connector workflow on demand.

When a file lands in the SFTP mirror bucket, an S3 event notification fires. This event flows through a message queue (SQS) into a Kafka topic. A streaming SQL engine (ksqlDB) materializes these events into a table — essentially "which connectors have new data waiting." A CronWorkflow runs every few minutes, queries that table, checks which connectors are eligible to run, and submits workflow jobs.

### Key Technical Points

- **Event-driven vs. polling**: Polling wastes compute checking buckets that may not have changed. Event-driven means connectors fire only when needed.
- **Kafka as the event backbone**: S3 events → SQS → Kafka bridge → ksqlDB materialized view. This pattern decouples file arrival from connector execution.
- **Concurrency guard**: Before triggering a connector, the scheduler checks whether one is already running for that source. This prevents overlapping runs that would corrupt in-progress state.
- **ConfigMap as the control plane**: Each connector's configuration (enabled/disabled, event-driven or cron-only, scheduling flags) lives in a Kubernetes ConfigMap. The scheduler reads this before submitting any workflow. Changing a flag in the ConfigMap takes effect on the next scheduling cycle.

### Interview Angle

*"How do you scale ingestion across hundreds of data sources?"* — You centralize the scheduling brain and decentralize the execution. One scheduler queries a materialized view of pending work and fans out to hundreds of parallel connector pods. Each pod knows nothing about the others.

---

## Layer 2 — Ingestion (NiFi Connector Layer)

### What Happens

This is where raw bytes become structured, parseable records. Each connector is a **NiFi instance** running as a Kubernetes pod. It picks up files from object storage, runs them through a processing pipeline, and writes the output to a downstream store.

The NiFi pipeline has several sequential stages:

**Stage 1: Spout (File Acquisition)**  
The connector reads from the inbound prefix in object storage. Files are fetched into NiFi's internal flow as FlowFiles. The file is now "in-flight."

**Stage 2: Decrypt**  
Source files are often PGP-encrypted at rest. The connector decrypts them using the customer's key. Failures at this stage land in an error folder.

**Stage 3: Decompress**  
Files may be gzipped, zipped, or tarred. Decompression happens here.

**Stage 4: Normalize**  
This is the most complex step. Normalization handles:
- **Format detection**: Is this comma-delimited? Pipe-delimited? Fixed-width? Does it have a header row? How many footer rows should be skipped?
- **Format conversion**: HL7 messages are converted to intermediate XML via XSLT transforms. EDI/X12 is flattened to CSV. XML documents are flattened. The output is always tabular.
- **Preprocess scripts**: Groovy scripts that handle source-specific oddities — prepending a batch key column, handling encoding issues, stripping BOM characters, reordering columns.

**Stage 5: Load to Staging Store**  
The normalized, tabular output is written to an intermediate store. For standard connectors this is a Cassandra/Scylla cluster (Extract Scylla). For streaming/v2 connectors, the XSLT transform happens in NiFi itself and output goes directly to a silver staging area.

### Key Technical Points

- **WIP folder tracking**: Every file's position in the pipeline is tracked by its presence in a `wip/` folder hierarchy. If a connector dies mid-run, you can tell exactly where each file was when it failed.
- **Error isolation**: A failure on one file does not block others. Failed files are moved to an `errors/` subfolder and can be reprocessed selectively.
- **Custom NiFi processors (NARs)**: Standard NiFi doesn't know how to write to Cassandra/Scylla or handle Arcadia's specific Avro schema. Custom NAR extensions provide these capabilities.
- **Two connector generations**:
  - **v1 (Standard)**: Batch-oriented. Picks up files from S3, runs them through normalize → staging-cassandra. Writes to Extract Scylla for downstream Spark transforms.
  - **v2 (Streaming)**: Event-oriented. Reads from Kafka, uses XSLT transforms inside NiFi, skips Scylla entirely. Output goes directly to silver staging (parquet on S3).
- **File size limits**: Extremely large files (multi-GB) can cause OOM errors in the JVM during normalization. The norm is to ask sources to split large files.

### What DE Should Know for Interviews

- NiFi is a **flow-based programming model** — you build a directed graph of processors. Each processor does one thing (decrypt, decompress, convert format, route, write). Failure handling is configured per connection (route errors to a different queue).
- **Idempotency at this layer** is achieved through state files. If you clear the state files and re-run the connector, it will reprocess all historical files. This is how you do a historical backfill or re-ingest after a transform bug fix.
- **The connector is not stateless**. It tracks which files it has processed. This state is stored as zero-byte marker files in object storage — simple, durable, and inspectable.

---

## Layer 3 — Extract Layer (Bronze Raw)

### What Happens

After NiFi normalization, for standard connectors, the tabular data is written to a structured parquet layout in object storage. This is the **Extract** (sometimes called Bronze Extract or Tabular Extract) layer.

This is the earliest queryable form of the data. It is **not deduplicated**. If a source sends the same patient record twice (in two different file drops), both copies exist in Extract.

### Key Technical Points

- **Partitioning scheme**: Data is partitioned by `EHR/transform name → data type → year → month → day → source`. This enables time-range scans without full table reads.
- **Format**: Parquet. Columnar storage, efficient for analytical queries.
- **Glue catalog**: The S3 partitions are registered in the AWS Glue Data Catalog, making them queryable via Athena. New S3 partitions added after table creation require a `MSCK REPAIR TABLE` command to be picked up by Athena.
- **Source column**: A `_arcadia_source` column on every row identifies which connector source contributed that row. Always lowercase. When doing cross-table joins, filter this column on both sides or you get silent data inflation.
- **Audit use case**: The Extract layer is the authoritative record of what was received from a source and when. If a source claims they sent data, you can prove or disprove it here by checking S3 timestamps and partition dates.

### What DE Should Know for Interviews

- Extract is the "raw archive." You never update it — it's append-only.
- The distinction between **file ingestion date** (S3 timestamp) and **data period** (the dates inside the file) is critical. A file landed on March 1st may contain claims from January 2023 (a backfill). These are independent dimensions.
- Extract tables exist in a separate Athena database (`us-west-1` in this platform's case) from the downstream Bronze/Silver tables (`us-east-1`). Region matters when writing Athena queries that join layers.

---

## Layer 4 — Origin Layer (Bronze Deduplicated)

### What Happens

The Origin layer is the **first deduplicated, clean view of the raw data**. It is written by an **Apache Hudi DeltaStreamer** job (called Origin Sync) that reads from the Extract parquet files.

Origin applies **Table Key Mappings (TKM)** — a configuration that defines what constitutes a unique record for each entity type. The Hudi DeltaStreamer uses these keys to perform an upsert: if the same record arrives twice (same primary key), it's deduplicated rather than duplicated.

### Key Technical Points

- **Hudi format**: Origin tables use Apache Hudi Copy-on-Write (CoW). This means:
  - Every record has a `_hoodie_commit_time` tracking when it was last written.
  - Updates create new parquet files; old versions are retained for time-travel queries.
  - Compaction jobs periodically merge delta files for query performance.
- **TKM (Table Key Mapping)**: For each entity (e.g., `encounter`, `claim_header`), the TKM defines the composite key that uniquely identifies a record. The deduplication logic uses this key. Getting TKM wrong causes either over-deduplication (records merged that shouldn't be) or under-deduplication (duplicates survive).
- **Independent from Scylla**: Origin reads directly from Extract S3, not from Extract Scylla. The two paths (Origin and the Scylla-based Silver path) are independent consumers of the same Extract data. A Scylla load failure does not affect Origin.
- **Athena and Redshift access**: Origin is queryable from both Athena (`bronze_origin_v1` database) and Redshift (via external schema, `origin` schema).

### What DE Should Know for Interviews

- **Why have both Extract and Origin?** Extract is the raw archive — no dedup, append-only, fastest to write. Origin is the reconciled view — deduplicated, Hudi-managed, slower to write but cleaner to query. You keep both because they serve different purposes: Extract for auditing, Origin for downstream joins.
- **Hudi CoW vs MoR**: Copy-on-Write rewrites the entire file on every update. Merge-on-Read writes deltas separately and merges at read time. CoW is better for read-heavy workloads (most analytical queries). MoR is better for high-update-rate streams. Origin uses CoW because it's query-heavy.

---

## Layer 5 — Extract Scylla (Intermediate Staging Store)

### What Happens

For the standard (non-streaming) connector path, after NiFi normalization, data is written to **Extract Scylla** — an Apache Cassandra cluster. This acts as the read-source for the Spark transformation jobs.

This is a specialized store, not the final destination. Think of it as a high-throughput staging database that buffers data between the file-based ingestion layer and the compute-heavy transformation layer.

### Key Technical Points

- **Why Cassandra at this stage?** Cassandra handles high write throughput from many parallel NiFi connectors without write contention. It stores data in a wide-column format that the Spark jobs can scan efficiently.
- **Not the source of truth**: Extract Scylla is transient. Data there is not deduplicated, not enriched, and may be stale if a connector ran multiple times. It's a staging buffer, not an archive.
- **Scylla, not vanilla Cassandra**: Scylla is a drop-in replacement for Cassandra written in C++. Higher throughput, lower latency, same API.
- **Access**: Primarily accessed via Zeppelin notebooks for debugging. Not queryable via Athena or Redshift — you need Cassandra CQL.

---

## Layer 6 — Spark Transform → Silver WRK (Pre-Enrichment Staging)

### What Happens

This is the compute-heavy step where raw tabular data becomes domain-structured entities. **Spark jobs** (running on Kubernetes via the Spark Operator) read from Extract Scylla, apply the connector's **transform logic**, and write the output to the **Silver WRK** (work/staging) layer.

The transform logic is defined per connector type and handles:
- **Column mapping**: Renaming, reordering, and casting source columns to match the Inspec schema.
- **Derived columns**: Computing values not present in the source — e.g., calculating age from date of birth, deriving a service type code from procedure codes.
- **PK generation**: Creating stable, deterministic primary keys from the source's natural key fields. This is usually a hash of the composite natural key.
- **Entity fan-out**: A single source record can produce multiple entity rows. An encounter in an EHR file might generate rows in `encounter`, `diagnosis`, `procedure`, and `provider` tables simultaneously.
- **Filtering**: Records that don't meet quality thresholds or don't match expected formats are dropped or quarantined.

### Key Technical Points

- **Silver WRK schema**: Output tables follow the **Inspec schema** — a standardized domain model with consistent column names across all connectors. `encounter`, `result`, `patient`, `plan_member_elig`, `plan_claim_header` are examples of Inspec entities.
- **Format**: Plain Parquet — no Hudi metadata. No `.hoodie/` directory. No `_hoodie_commit_time`.
- **No term mapping yet**: Coded values (ICD codes, CPT codes, LOINC codes) are not yet translated to display names. Raw codes from the source are preserved.
- **No delete-by-absence yet**: Silver WRK is additive. Records are inserted or upserted but never logically deleted at this stage.
- **Partitioning**: `data type → availability → source`. The `availability` dimension (`alpha`, `beta`, `ga`) is the promotion lifecycle gate — data starts as `alpha`, gets promoted to `beta` after initial QA, and to `ga` after full validation.
- **Debugging role**: If data looks wrong in the final Silver layer, you drop to Silver WRK to isolate whether the problem is in the transform or in the downstream enrichment step.

### What DE Should Know for Interviews

- **Spark on Kubernetes**: The Spark Operator manages Spark driver/executor pods on Kubernetes. Each transform job spins up a driver pod and N executor pods. The driver coordinates, executors do the work in parallel. After the job completes, all pods terminate.
- **Transformation is not just renaming columns**: It's applying business logic — computing derived fields, generating primary keys, splitting multi-entity source rows, applying data quality filters. A single transform can have thousands of lines of Scala/Python logic.
- **Why WRK is separate from Silver**: Silver WRK is the "raw transform output." It lets you validate the transform in isolation before the enrichment step. If a column mapping is wrong, you can find it in WRK without having to wait for enrichment to complete.

---

## Layer 7 — Silver (Enriched, Source of Truth)

### What Happens

Silver is the **final, production-quality layer**. It is the source of truth for all downstream consumers — data warehouse loads, analytics, quality measure calculations, care management platforms.

Getting from Silver WRK to Silver involves the **Source Load Workflow (SLW)** — a job (or job chain) that reads from Silver WRK and applies enrichment steps before writing the final records as **Apache Hudi** tables.

### Enrichment Steps

**Term Mapping**  
Coded values are resolved to human-readable display names and standardized codes. A raw ICD-10 code `J18.9` becomes `Pneumonia, unspecified organism`. LOINC codes are mapped to lab test names. CPT codes are mapped to procedure descriptions. This mapping uses lookup tables maintained by the platform's clinical content team.

**Delete-by-Absence (DBA)**  
When a source sends a full refresh (not a delta), records that were previously present but are absent in the new delivery should be marked as deleted. DBA compares the set of records written in the current batch against the existing Silver records for that source, and soft-deletes records that no longer appear.  
- Soft delete = setting `delete_ind = '1'` on the record, not physical deletion.  
- This preserves historical audit trails while keeping active queries clean (`WHERE delete_ind = '0'`).

**Hudi Upsert**  
Silver tables are written in Hudi Copy-on-Write format. Every write is an upsert against the Hudi table:
- If the record's PK already exists in Silver, the existing row is updated.
- If the record is new, a new row is inserted.
- Hudi tracks commit history via `.hoodie/` metadata. You can query `_hoodie_commit_time` to see when a record was last written.

### Key Technical Points

- **Silver WRK vs Silver**: The critical distinction is that Silver WRK has raw codes, no delete logic, and plain parquet. Silver has mapped codes, delete logic, and Hudi. Never validate what a customer sees by looking at Silver WRK — it will mislead you.
- **Availability partitions**: `ga` (generally available) = data visible to all users. `beta` = data visible only to internal teams for validation. `alpha` = data just landed, not yet exposed. The promotion from alpha → beta → ga is gated by QA checks.
- **Domain split**: Silver is split by domain type. Clinical entities (`encounter`, `result`, `patient`, `diagnosis`) are in `silver_clinical_v2`. Claims entities (`plan_member_elig`, `plan_claim_header`, `plan_claim_line`) are in `silver_claims_v2`. Querying the wrong database type returns nothing.
- **Athena vs Redshift naming**: In Athena, Silver tables are named by entity (e.g., `encounter`, `plan_member_elig`). In Redshift's `inspec` schema, clinical entities are prefixed with `t_` (e.g., `t_encounter`) and claims entities with `plan_` (e.g., `plan_member_elig`). Knowing these mappings is essential for cross-layer validation.
- **`delete_ind` value difference**: Athena Silver uses `'0'` for active and `'1'` for deleted. Redshift inspec uses `'N'` for active and `'Y'` for deleted. Mixing these up causes silent zero-row results.
- **`orig_` prefix convention**: When Silver data is loaded into the QDW data warehouse, ID columns are renamed with an `orig_` prefix (e.g., `member_id` → `orig_member_id`). The warehouse assigns its own integer surrogate key to the bare column name. This is specific to the QDW layer — Athena Silver never uses `orig_` prefix.

### What DE Should Know for Interviews

- **Why Hudi?** Hudi solves three problems at once: upsert semantics on object storage (S3 doesn't natively support row-level updates), time-travel queries (you can query "what did Silver look like at midnight yesterday?"), and incremental processing (downstream jobs can consume only records changed since their last run by filtering on `_hoodie_commit_time`).
- **Why soft deletes?** Hard-deleting records from an analytics lakehouse causes compaction and partition complexity. Soft deletes (`delete_ind = '1'`) keep the history intact for audit, allow rollback if the delete was wrong, and maintain consistent row counts across time-travel queries.
- **Silver is the contract**: Everything downstream (warehouse, analytics, reporting) trusts Silver as the authoritative source. If Silver is wrong, everything built on it is wrong. This is why the enrichment step (term mapping, DBA, Hudi upsert) is so heavily tested.

---

## Summary: Layer Comparison Table

| Layer | What It Is | Format | Deduplicated | Term-Mapped | Delete Logic | Primary Query Tool |
|-------|-----------|--------|--------------|-------------|--------------|-------------------|
| **Inbound (SFTP Mirror)** | Raw files as received | Any (CSV, HL7, EDI, XML, Avro) | No | No | No | S3 CLI / file browser |
| **WIP / Staging** | Files in transit through NiFi | Binary / intermediate | No | No | No | S3 CLI |
| **Extract (Bronze Raw)** | Post-NiFi tabular data | Parquet | No | No | No | Athena |
| **Origin (Bronze Deduped)** | Deduped extract, TKM applied | Hudi CoW Parquet | Yes | No | No | Athena / Redshift |
| **Extract Scylla** | Staging buffer for Spark | Cassandra wide-column | No | No | No | CQL (Zeppelin) |
| **Silver WRK** | Post-Spark transform, pre-enrichment | Plain Parquet | Partial (TKM-level) | No | No | Athena |
| **Silver (Enriched)** | Final production-quality entities | Hudi CoW Parquet | Yes (Hudi upsert) | Yes | Yes (soft delete) | Athena / Redshift |

---

## Common Interview Questions and How to Answer Them

### "Why do you need both Extract and Silver? Isn't that redundant?"

They serve different purposes. Extract is the raw archive — it proves what was received, when, and from whom. It's append-only and immutable. Silver is the operational truth — deduplicated, enriched, maintained with upsert semantics. You need Extract for auditing and debugging; you need Silver for everything downstream.

### "How do you handle late-arriving data?"

Late-arriving data (a file sent 3 months after the reporting period) lands in Extract with today's S3 timestamp but with old period dates inside the file. The transform picks it up in the next run, generates Silver WRK rows with the historical dates, and the SLW upserts them into Silver. Because Silver uses Hudi upserts keyed on entity ID, the late data merges cleanly with existing records rather than duplicating them.

### "What happens if the transform job fails halfway through?"

Silver WRK is written atomically per partition. A failed Spark job leaves incomplete WRK partitions that are never promoted to Silver. The job can be rerun — it reads from Scylla again and rewrites WRK from scratch. Because the SLW only runs after a successful transform, Silver stays clean. The gap is visibility latency — data sits in Scylla until the job succeeds.

### "How do you debug a data quality issue reported by a business user?"

Work backwards through the layers:
1. Confirm what the user sees in the reporting tool (Foundry/QDW).
2. Check Silver (`silver_v2`) — is the record there? Is it correctly enriched? What's its `_hoodie_commit_time`?
3. If Silver is wrong, check Silver WRK — was the transform output correct?
4. If WRK is wrong, check Extract — was the raw data from the source correct?
5. If Extract is missing, check SFTP mirror — did the file arrive?
6. If the file arrived but extract is missing, the NiFi connector failed — check WIP errors.

### "What is the role of Kafka in this pipeline?"

Kafka is the event backbone. It decouples file arrival (SFTP → S3) from ingestion (NiFi connectors). S3 events flow through SQS → Kafka → ksqlDB → scheduling workflow. This means the scheduler has a materialized, queryable view of "which connectors have new data" rather than polling hundreds of S3 paths. Kafka also enables at-least-once delivery semantics — events are retained and can be replayed if a consumer fails.

---

## Appendix: Key Technologies Referenced

| Technology | Role in Pipeline |
|-----------|-----------------|
| **Apache NiFi** | Data ingestion engine — file routing, format conversion, normalize |
| **Apache Kafka** | Event streaming backbone — S3 event notifications, connector scheduling |
| **ksqlDB** | Streaming SQL on Kafka — materializes "connectors to run" view |
| **Apache Cassandra / Scylla** | Extract Scylla — high-throughput staging store between NiFi and Spark |
| **Apache Spark** | Batch transformation engine — reshape raw data into Inspec entities |
| **Apache Hudi** | Data lakehouse table format — upserts, CoW, time-travel on S3 |
| **AWS S3** | Primary data lake storage — all layers live here |
| **AWS Athena** | Serverless query on S3 Parquet/Hudi — used for all Silver/Bronze queries |
| **Amazon Redshift** | Data warehouse — Silver data loaded via external schemas |
| **Kubernetes / Argo Workflows** | Container orchestration and workflow engine for all pipeline jobs |
| **AWS Glue** | Metadata catalog — partition registration for Athena |
| **XSLT** | XML transform language — converts HL7/CDA/EDI to tabular format inside NiFi |
