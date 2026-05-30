# Data Pipeline Architecture — Mermaid Diagrams
### Inbound → Bronze → Silver

---

## Diagram 1 — Full Pipeline Overview (End-to-End)

**Question it answers:** *How does data flow from a source system to the Silver layer, and what are the major checkpoints?*

```mermaid
flowchart TB
    subgraph sources ["Source Systems"]
        EHR["EHR Platforms\n(Epic, eCW, Athena, etc.)"]
        PAYER["Payers / Claims\n(EDI 837, CCLF, CSV)"]
        ADT["ADT Streams\n(HL7 v2 — real-time)"]
    end

    subgraph inbound ["Layer 0 — Inbound Delivery"]
        SFTP["SFTP Server\n(customer-managed)"]
        MIRROR["SFTP Mirror Agent\n(continuous sync)"]
        S3IN["S3: Inbound Prefix\n(raw files, encrypted)"]
        STATE["State Files\n(zero-byte markers, idempotency)"]
    end

    subgraph eventing ["Layer 1 — Event-Driven Scheduling"]
        S3EVT["S3 Event Notification"]
        SQS["SQS Queue"]
        KAFKA["Kafka Topic\n(inbound-file-events)"]
        KSQL["ksqlDB\n(connectors_to_run view)"]
        SCHED["Scheduler CronWorkflow\n(every 5 min)"]
    end

    subgraph ingestion ["Layer 2 — NiFi Connector (Ingestion)"]
        SPOUT["Spout\n(List + Fetch files from S3)"]
        DECRYPT["Decrypt\n(PGP keys)"]
        DECOMP["Decompress\n(gzip / zip / tar)"]
        NORM["Normalize\n(format detection, XSLT transforms,\npreprocess scripts)"]
        WIP["WIP Folder Tracking\n(S3 in-progress markers)"]
        ERR["Error Folder\n(failed files isolated)"]
    end

    subgraph bronze ["Layer 3–4 — Bronze"]
        EXT["Extract (Tabular)\nRaw Parquet on S3\nPartitioned: EHR → entity → date → source\nNOT deduplicated"]
        SCYLLA["Extract Scylla\n(Cassandra staging buffer)\nHigh-write-throughput\nRead by Spark transforms"]
        ORIGIN["Origin (Bronze Deduplicated)\nHudi CoW Parquet\nTKM applied — deduped by entity PK\nQueryable via Athena + Redshift"]
    end

    subgraph silver ["Layer 5–7 — Silver"]
        SPARK["Spark Transform Job\n(Kubernetes Spark Operator)\nColumn mapping, derived fields,\nPK generation, entity fan-out"]
        SWRK["Silver WRK\n(Pre-enrichment staging)\nPlain Parquet — no Hudi\nNo term mapping, no delete logic\nUse for transform debugging only"]
        SLW["Source Load Workflow\n(Enrichment Step)\nTerm mapping (ICD→display)\nDelete-by-absence\nHudi upsert"]
        SILV["Silver (Enriched)\nHudi CoW Parquet\nTerm-mapped + soft-delete\nAvailability: alpha → beta → ga\nSOURCE OF TRUTH"]
    end

    subgraph downstream ["Downstream Consumers"]
        ATHENA["Athena\n(silver_clinical_v2\nsilver_claims_v2)"]
        REDSHIFT["Redshift\n(inspec schema\nt_encounter, plan_member_elig)"]
        DW["Data Warehouse / QDW\n(MSSQL, surrogate keys,\norig_ prefix on IDs)"]
        ANALYTICS["Analytics / Reporting\n(Foundry, dashboards, measures)"]
    end

    EHR --> SFTP
    PAYER --> SFTP
    ADT --> SFTP
    SFTP --> MIRROR --> S3IN
    S3IN --> STATE

    S3IN --> S3EVT --> SQS --> KAFKA --> KSQL --> SCHED

    SCHED -->|"trigger connector workflow\n(Argo Workflow)"| SPOUT
    S3IN --> SPOUT

    SPOUT --> DECRYPT --> DECOMP --> NORM
    NORM --> WIP
    NORM --> ERR

    NORM -->|"Standard connector\n(write tabular parquet)"| EXT
    NORM -->|"Standard connector\n(write to staging DB)"| SCYLLA

    EXT -->|"Hudi DeltaStreamer\nOrigin Sync job"| ORIGIN

    SCYLLA -->|"Spark reads\nScylla tables"| SPARK
    SPARK --> SWRK

    SWRK -->|"SLW reads\nsilver_wrk"| SLW
    SLW --> SILV

    SILV --> ATHENA
    SILV --> REDSHIFT
    REDSHIFT --> DW
    ATHENA --> ANALYTICS
    REDSHIFT --> ANALYTICS
```

**Architecture takeaways:**
- NiFi is the **ingestion boundary** — everything before it is delivery, everything after is transformation
- **Two independent paths** run from Extract: one to Origin (Bronze dedup), one to Scylla → Spark → Silver
- Silver WRK is a **staging area, not a data product** — enrich before exposing downstream
- Hudi is used at **Origin** and **Silver** for upsert semantics and time-travel
- The Kafka/ksqlDB/Scheduler pattern decouples **file arrival** from **connector execution**

---

## Diagram 2 — NiFi Connector Internals (Ingestion Deep Dive)

**Question it answers:** *What exactly happens inside a single connector run from file pickup to output?*

```mermaid
flowchart TB
    subgraph trigger ["Trigger"]
        CRON["Scheduler detects new files\n(ksqlDB query → Argo submit)"]
        POD["NiFi Pod Starts\n(Kubernetes — Argo namespace)"]
    end

    subgraph spout ["Spout Phase"]
        LIST["ListS3 — scan inbound prefix\n(checks state files for already-processed)"]
        FETCH["FetchS3 — download file bytes"]
        TRACK["Write WIP marker\n(file is now in-flight)"]
    end

    subgraph process ["Processing Phase"]
        DEC["Decrypt\n(PGP private key)"]
        DCOMP["Decompress\n(gzip / zip)"]
        PRE["Preprocess Script\n(Groovy — fix encoding, prepend batch key)"]
        FMT{"Format?"}
        CSV["CSV → validate headers\ndetect delimiter"]
        HL7["HL7 → XSLT → XML → CSV"]
        EDI["EDI/X12 → flatten → CSV"]
        XML["XML/CDA → XSLT → flatten → CSV"]
        AVRO["Avro → deserialize → CSV"]
    end

    subgraph output ["Output Phase"]
        STAGE["Staging-Cassandra\n(batched write to Extract Scylla)"]
        EXTRACT_S3["Write Parquet\n(tabular extract prefix on S3)"]
        STATEWRITE["Write state file\n(zero-byte marker — prevents reprocess)"]
        DONE["WIP marker removed\n(file complete)"]
    end

    subgraph errors ["Error Handling"]
        ERRFOLD["wip/errors/ folder\n(failed file moved here)"]
        REPROCESS["Reprocess-Errors flow\n(manual retry)"]
    end

    CRON --> POD --> LIST --> FETCH --> TRACK
    TRACK --> DEC --> DCOMP --> PRE --> FMT
    FMT -->|CSV| CSV
    FMT -->|HL7| HL7
    FMT -->|EDI| EDI
    FMT -->|XML| XML
    FMT -->|Avro| AVRO
    CSV --> STAGE
    HL7 --> STAGE
    EDI --> STAGE
    XML --> STAGE
    AVRO --> STAGE
    STAGE --> EXTRACT_S3
    EXTRACT_S3 --> STATEWRITE --> DONE

    DEC -->|failure| ERRFOLD
    DCOMP -->|failure| ERRFOLD
    PRE -->|failure| ERRFOLD
    STAGE -->|failure| ERRFOLD
    ERRFOLD --> REPROCESS
```

**Connector internals takeaways:**
- **State files** are the idempotency mechanism — one zero-byte marker per processed file
- **WIP folder** is the progress tracker — a file stuck in WIP means the run failed mid-flight
- Format conversion happens **inside NiFi** before any Spark job runs
- Errors are **isolated per file** — one bad file cannot block the others
- The connector pod **terminates after the run** — it is not a long-lived process (for batch connectors)

---

## Diagram 3 — Bronze to Silver Transformation Flow

**Question it answers:** *How does raw Extract data become enriched Silver data?*

```mermaid
flowchart TB
    subgraph extract ["Bronze — Extract (Raw)"]
        EXT_S3["Tabular Extract\nS3 Parquet\nPartitioned by: EHR → entity → date → source\nNot deduplicated"]
        SCYLLA["Extract Scylla\n(Cassandra)\nStaging buffer — high write throughput\nLoaded independently by Scylla Loader"]
    end

    subgraph origin ["Bronze — Origin (Deduplicated)"]
        HUDI_O["Hudi DeltaStreamer\n(Origin Sync Job)"]
        ORIG["Origin Tables\nHudi CoW Parquet\nTKM applied (entity PK dedup)\nQueryable via Athena + Redshift\nPart of audit lineage"]
    end

    subgraph transform ["Silver WRK — Transform Stage"]
        SPARK_JOB["Spark Transform Job\n(Kubernetes Spark Operator)"]
        MAPPING["Column Mapping\n(source col → Inspec schema col)"]
        DERIVED["Derived Fields\n(age, service type, computed flags)"]
        PKGEN["PK Generation\n(deterministic hash of natural keys)"]
        FANOUT["Entity Fan-out\n(1 source row → N entity rows)"]
        FILTER["Data Quality Filter\n(drop malformed records)"]
        SWRK["Silver WRK\nPlain Parquet — no Hudi\nNo term mapping\nNo delete logic\nAvailability partitions: alpha/beta/ga\nFor debugging only"]
    end

    subgraph enrichment ["Silver — Enrichment Stage (SLW)"]
        TERMMAP["Term Mapping\n(ICD codes → display names\nLOINC → lab names, CPT → procedure names)"]
        DBA["Delete-by-Absence\n(soft-delete records absent from full refresh\ndelete_ind = '1')"]
        HUDI_U["Hudi Upsert\n(CoW — update existing or insert new\nkeyed on entity PK)"]
        SILV["Silver (Enriched)\nHudi CoW Parquet\nAvailability: alpha → beta → ga (promotion gates)\ndelete_ind: '0' active / '1' deleted\n_hoodie_commit_time for recency check\nSOURCE OF TRUTH"]
    end

    subgraph debug ["Debugging Reference Points"]
        D1["Issue in Silver?\nCheck Silver WRK — same record wrong?\n↓ Problem is in transform"]
        D2["WRK correct but Silver wrong?\n↓ Problem is in enrichment / SLW"]
        D3["WRK missing?\n↓ Check Extract / Scylla\n↓ Check NiFi WIP errors"]
    end

    EXT_S3 --> HUDI_O --> ORIG
    EXT_S3 -.->|"independent path\n(not via Origin)"| SCYLLA
    SCYLLA --> SPARK_JOB
    SPARK_JOB --> MAPPING --> DERIVED --> PKGEN --> FANOUT --> FILTER --> SWRK

    SWRK --> TERMMAP --> DBA --> HUDI_U --> SILV

    SILV -.-> D1
    SWRK -.-> D2
    EXT_S3 -.-> D3
```

**Transformation takeaways:**
- **Extract → Origin** is a separate path from **Extract → Scylla → Spark → Silver**. Origin does not feed into Silver.
- Silver WRK has **no enrichment** — it's raw transform output used for debugging
- The enrichment step (SLW) does three things: **term mapping**, **delete-by-absence**, **Hudi upsert**
- **Availability gates** (alpha → beta → ga) are the QA promotion mechanism before data is exposed to users
- `_hoodie_commit_time` is how you verify Silver recency — always start here when investigating freshness issues

---

## Diagram 4 — Layer Access & Query Reference

**Question it answers:** *As a DE, where do I query data at each layer?*

```mermaid
flowchart LR
    subgraph layers ["Pipeline Layers"]
        L0["Inbound Files"]
        L1["Extract (Bronze Raw)"]
        L2["Origin (Bronze Deduped)"]
        L3["Silver WRK"]
        L4["Silver (Enriched)"]
        L5["Redshift Inspec"]
        L6["QDW / Data Warehouse"]
    end

    subgraph tools ["Query Tools & Locations"]
        T0["AWS S3 CLI\ns3://sftp-mirror/inbound/{customer}/{source}/"]
        T1["Athena — us-west-1\n{customer}_{ns}_extract\nTable: {ehr}__{datatype}\nMSCK REPAIR before query"]
        T2["Athena — us-east-1\n{infra}_{ns}_{customer}_bronze_origin_v1\nTable: {ehr}__{datatype}\nHudi — filter _hoodie_commit_time"]
        T3["Athena — us-east-1\n{infra}_{ns}_{customer}_silver_{type}_wrk_v3\nPlain Parquet\nCheck S3 timestamps for recency"]
        T4["Athena — us-east-1\n{infra}_{ns}_{customer}_silver_{type}_v2\nHudi — use _hoodie_commit_time\ndelete_ind: '0'=active '1'=deleted"]
        T5["Redshift\n{customer}_reporting_prd{NN}\nSchema: inspec\nt_{entity} (clinical)\nplan_{entity} (claims)\ndelete_ind: 'N'=active 'Y'=deleted"]
        T6["MSSQL / QDW\nSchema: dbo\nID columns renamed to orig_{col}\nSurrogate int PK replaces natural key"]
    end

    L0 --> T0
    L1 --> T1
    L2 --> T2
    L3 --> T3
    L4 --> T4
    L5 --> T5
    L6 --> T6
```

**Query access takeaways:**
- Extract is in a **different Athena region** (us-west-1) from everything else (us-east-1) — cross-region joins require care
- **Always run `MSCK REPAIR TABLE`** before querying Extract in Athena — S3 partitions must be registered
- Silver WRK has **no `_hoodie_commit_time`** — use S3 object timestamps to check recency
- `delete_ind` values differ between **Athena Silver** (`'0'`/`'1'`) and **Redshift inspec** (`'N'`/`'Y'`) — mixing them causes silent zero-row results
- QDW renames ID columns with `orig_` prefix — `member_id` in Silver becomes `orig_member_id` in QDW

---

## How the 4 Diagrams Fit Together

| Diagram | Lens | Think of it as |
|---------|------|---------------|
| **1. Full Pipeline Overview** | Macro end-to-end | The complete data journey from SFTP to Silver |
| **2. NiFi Connector Internals** | Ingestion deep dive | What happens inside one connector run |
| **3. Bronze to Silver Transform** | Transformation detail | How raw data becomes enriched domain entities |
| **4. Layer Access Reference** | Operations | Where to query data at each layer for debugging |

---

## One-Liner for Each Layer (Interview Ready)

| Layer | One-liner |
|-------|-----------|
| **Inbound** | Raw files dropped by source systems, mirrored to S3, idempotency tracked by state files |
| **NiFi Connector** | Decrypts, decompresses, normalizes, and converts formats before loading to staging |
| **Extract (Bronze Raw)** | Append-only raw parquet archive — proof of what was received, when, and from whom |
| **Origin (Bronze Deduped)** | TKM-keyed Hudi dedup on top of Extract — first clean, queryable view of raw data |
| **Extract Scylla** | High-throughput Cassandra buffer between NiFi and Spark — transient, not a source of truth |
| **Silver WRK** | Spark transform output in plain parquet — correct schema, raw codes, no enrichment |
| **Silver (Enriched)** | Hudi upsert with term mapping and delete-by-absence — production source of truth |
