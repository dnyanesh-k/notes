# Q12: Design Document Processing Pipeline

---

## Clarifying Questions

What types of documents are we processing — PDFs, scanned images (OCR needed), Word files, HTML? The preprocessing steps differ dramatically between machine-readable text and scanned images.

What's the processing goal — extraction (pull structured data from free text), classification (label the document type), transformation (convert format), or all three? This determines the pipeline stages.

What's the volume — a few hundred documents per day or millions? And what are the latency requirements — is processing triggered on upload (real-time, seconds) or is nightly batch acceptable?

Do we need human-in-the-loop for low-confidence extractions, or is fully automated processing required?

*Assuming: mixed document types (PDFs, scanned images, Word files), multi-stage processing (OCR → extraction → classification → structured output), 500K documents/day, processing within 5 minutes of upload, human review for low-confidence results.*

---

## Scope

I'll design a scalable, multi-stage document processing pipeline with: ingestion, OCR for scanned documents, structured data extraction, classification, quality scoring, and routing for human review. Each stage is decoupled via queues so stages can scale and fail independently.

---

## High Level Design

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSING PIPELINE                              │
│                                                                              │
│  Upload ──▶ S3 ──▶ SQS ──▶ ┌───────────────────────────────────────────┐  │
│                              │         Stage 1: Pre-processing           │  │
│                              │  Detect type → PDF/Image/Word             │  │
│                              │  PDF text extraction (PyMuPDF)            │  │
│                              │  Image → OCR queue (Tesseract/AWS Textract)│  │
│                              └─────────────────┬─────────────────────────┘  │
│                                                 │ (clean text)               │
│                                                 ▼                            │
│                              ┌───────────────────────────────────────────┐  │
│                              │       Stage 2: Information Extraction      │  │
│                              │  Named Entity Recognition (spaCy, BERT)   │  │
│                              │  Key-value extraction (dates, amounts,     │  │
│                              │  names, addresses)                         │  │
│                              │  Table detection and parsing               │  │
│                              └─────────────────┬─────────────────────────┘  │
│                                                 │ (structured JSON)          │
│                                                 ▼                            │
│                              ┌───────────────────────────────────────────┐  │
│                              │       Stage 3: Classification & Scoring   │  │
│                              │  Document type classification              │  │
│                              │  Confidence scoring                        │  │
│                              │  Routing: auto-approve vs human review     │  │
│                              └─────────────────┬─────────────────────────┘  │
│                                                 │                            │
│                              ┌──────────────────┴───────────────┐           │
│                              ▼                                   ▼           │
│                    ┌──────────────────┐             ┌──────────────────────┐│
│                    │  Output Store    │             │   Human Review Queue ││
│                    │  (PostgreSQL +   │             │   (Review Dashboard)  ││
│                    │   S3 for files)  │             └──────────────────────┘│
│                    └──────────────────┘                                      │
└──────────────────────────────────────────────────────────────────────────────┘

Orchestration: each stage is a separate worker pool. All connected by SQS.
Monitoring: each document has a state machine — every stage transition logged.
```

---

## Deep Dive 1 — Stage 1: Pre-processing

### Document Type Detection

```python
def detect_type(s3_key: str, content_bytes: bytes) -> str:
    # Magic bytes detection — more reliable than file extension
    if content_bytes[:4] == b'%PDF':
        return 'pdf'
    if content_bytes[:2] in (b'BM', b'\xff\xd8'):  # BMP or JPEG
        return 'image'
    if content_bytes[:4] == b'PK\x03\x04':  # ZIP = DOCX/XLSX
        return 'docx'
    return 'unknown'
```

### PDF Processing

PDFs come in two types: text-based (most modern PDFs) and image-based (scanned, photographed documents).

```python
def extract_text_from_pdf(pdf_bytes: bytes) -> tuple[str, bool]:
    doc = fitz.open(stream=pdf_bytes)
    text = ""
    for page in doc:
        page_text = page.get_text()
        text += page_text
    
    is_scanned = len(text.strip()) < 100 and doc.page_count > 0
    return text, is_scanned

# If text too short → it's a scanned PDF → route to OCR stage
```

### OCR for Scanned Documents

OCR (Optical Character Recognition) converts image pixels to text. Two options:

**Tesseract (open source):** Free, runs locally. Accuracy: ~85-95% for clean scans, degrades on poor quality images. Speed: 1-5 seconds per page.

**AWS Textract (managed):** ~99% accuracy, handles tables and forms natively (detects key-value pairs in forms: "Name: John Smith"). More expensive ($0.015/page) but production-grade. Handles multi-column, handwriting, and complex layouts.

```python
def ocr_with_textract(image_bytes: bytes) -> dict:
    client = boto3.client('textract')
    response = client.analyze_document(
        Document={'Bytes': image_bytes},
        FeatureTypes=['TABLES', 'FORMS']  # detect tables and key-value pairs
    )
    
    # Extract text blocks
    text_blocks = [b['Text'] for b in response['Blocks'] if b['BlockType'] == 'LINE']
    full_text = '\n'.join(text_blocks)
    
    # Extract form key-value pairs
    kv_pairs = extract_key_value_pairs(response['Blocks'])
    
    # Extract table data
    tables = extract_tables(response['Blocks'])
    
    return { 'text': full_text, 'kv_pairs': kv_pairs, 'tables': tables }
```

**Image preprocessing before OCR (critical for quality):**
- Deskew: rotate slightly tilted images to be straight
- Denoise: remove scan artifacts (speckles, lines)
- Binarize: convert to black-and-white (increases contrast for OCR)
- DPI normalization: ensure at least 300 DPI (below this, OCR accuracy drops sharply)

Poor input → poor OCR → poor extraction. Preprocessing quality determines downstream accuracy.

---

## Deep Dive 2 — Stage 2: Information Extraction

After getting clean text, extract structured data.

### Named Entity Recognition (NER)

```python
import spacy
nlp = spacy.load("en_core_web_lg")

def extract_entities(text: str) -> dict:
    doc = nlp(text)
    return {
        'persons': [ent.text for ent in doc.ents if ent.label_ == 'PERSON'],
        'organizations': [ent.text for ent in doc.ents if ent.label_ == 'ORG'],
        'dates': [ent.text for ent in doc.ents if ent.label_ == 'DATE'],
        'money': [ent.text for ent in doc.ents if ent.label_ == 'MONEY'],
        'locations': [ent.text for ent in doc.ents if ent.label_ == 'GPE'],
    }
```

For domain-specific entities (legal clause types, medical terms, financial instruments), fine-tune a BERT model on domain-labeled data. spaCy's general model won't know that "Force Majeure" is a legal clause type.

### LLM-based Extraction for Complex Documents

For complex extraction tasks (extract specific clauses from a 50-page contract), LLMs outperform rule-based and NER approaches:

```python
extraction_prompt = f"""
Extract the following fields from this contract text. Return JSON only.
Fields: contract_date, parties, payment_terms, termination_clause, penalty_amount

Text:
{document_text[:4000]}  # truncate to fit context window

JSON output:
"""

result = llm.complete(extraction_prompt)
extracted = json.loads(result)
```

Cost: ~$0.05 per document with GPT-4. Justified for high-value documents (contracts, invoices). For simple documents (forms with clearly labeled fields), rule-based regex extraction is faster and cheaper.

### Confidence Scoring

Every extracted field gets a confidence score:

```python
def score_extraction(extracted: dict, raw_text: str) -> dict:
    scored = {}
    for field, value in extracted.items():
        if value is None:
            scored[field] = { 'value': None, 'confidence': 0.0 }
        elif value in raw_text:  # exact string match → high confidence
            scored[field] = { 'value': value, 'confidence': 0.95 }
        elif fuzzy_match(value, raw_text) > 0.8:  # close match
            scored[field] = { 'value': value, 'confidence': 0.75 }
        else:
            scored[field] = { 'value': value, 'confidence': 0.5 }
    return scored
```

For LLM-based extraction, add a separate validation step: re-extract the same fields with a different prompt, compare results. If they agree → high confidence. If they disagree → flag for human review.

---

## Deep Dive 3 — Stage 3: Classification and Routing

### Document Classification

```python
# Multi-class classification using fine-tuned BERT
classes = ['invoice', 'contract', 'tax_form', 'id_document', 'medical_record', 'other']

def classify_document(text: str) -> tuple[str, float]:
    inputs = tokenizer(text[:512], return_tensors='pt', truncation=True)
    outputs = classifier_model(**inputs)
    probs = softmax(outputs.logits)
    class_idx = argmax(probs)
    return classes[class_idx], probs[class_idx].item()

document_type, confidence = classify_document(extracted_text)
```

### Routing Decision

```python
AUTO_APPROVE_THRESHOLD = 0.85
HUMAN_REVIEW_THRESHOLD = 0.60

def route_document(extracted: dict, doc_type: str, confidence: float) -> str:
    if confidence < HUMAN_REVIEW_THRESHOLD:
        return 'human_review'  # too uncertain
    
    # Check field-level confidence
    low_confidence_fields = [
        field for field, data in extracted.items()
        if data['confidence'] < 0.70
    ]
    if len(low_confidence_fields) > 2:
        return 'human_review'  # too many uncertain fields
    
    if confidence >= AUTO_APPROVE_THRESHOLD:
        return 'auto_approve'
    
    return 'human_review'  # middle ground → human review
```

---

## Data Model and State Machine

```sql
CREATE TABLE documents (
    id              UUID PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    filename        VARCHAR(500) NOT NULL,
    s3_key          VARCHAR(1000) NOT NULL,
    file_type       VARCHAR(50),
    status          ENUM('uploaded','preprocessing','extracting','classifying',
                         'auto_approved','pending_review','reviewed','failed')
                    DEFAULT 'uploaded',
    document_type   VARCHAR(100),
    confidence      DECIMAL(4,3),
    extracted_data  JSON,
    error_message   TEXT,
    processing_started_at DATETIME,
    processing_completed_at DATETIME,
    created_at      DATETIME NOT NULL DEFAULT NOW(),
    INDEX idx_user_status (user_id, status),
    INDEX idx_status_created (status, created_at)
);

CREATE TABLE processing_events (
    id              BIGINT PRIMARY KEY AUTO_INCREMENT,
    document_id     UUID NOT NULL,
    stage           VARCHAR(100) NOT NULL,
    status          ENUM('started','completed','failed') NOT NULL,
    duration_ms     INT,
    error           TEXT,
    created_at      DATETIME NOT NULL,
    INDEX idx_document_id (document_id)
);
-- Every stage transition logged — full audit trail
```

---

## Scale — What Breaks at 10x?

At 5M documents/day = ~58 docs/sec:

**Pre-processing bottleneck:** OCR with Textract at 2-5 seconds/page, 10-page average = 20-50 seconds per document. At 58 docs/sec, need 58 × 30 seconds = 1,740 concurrent Textract calls. Textract has concurrency limits — use a queue-based pattern with auto-scaling workers that respect Textract's throughput limits. AWS Textract scales automatically but you pay per page. At 5M docs × 10 pages × $0.015/page = $750K/day. Use Tesseract for low-value documents, Textract for high-value ones.

**Extraction workers (LLM):** At $0.05/document and 5M/day = $250K/day. Not sustainable. Solutions: use LLM only for complex documents (< 20% of total), batch simpler documents through rule-based extraction, fine-tune a smaller open-source model on your domain-labeled data ($10K one-time cost vs $250K/day).

**PostgreSQL storage:** 5M rows/day with JSON extracted data (~10KB/row) = 50 GB/day. Use TimescaleDB or partition by month. Archive to S3 after 90 days (keep only metadata in DB, full extracted data in S3).

---

## Trade-offs

**Rule-based vs ML extraction:** Rules are fast, cheap, predictable, and easy to debug. They break on format variations (different invoice layouts). ML models handle variation but are a black box, require labeled training data, and drift over time (retrain quarterly). Best practice: use rules for well-structured documents with known formats, ML for varied or complex documents.

**Synchronous vs asynchronous pipeline:** Processing a document synchronously (user waits for the result) requires the pipeline to complete in < 2 seconds — almost impossible for OCR + ML extraction. Async is correct: user uploads, gets a job ID immediately, polls for status or receives a webhook when complete. The 5-minute SLA for completion is achievable with async.

**Error handling:** Every stage can fail. The document state machine tracks which stage failed. Retry logic is per-stage: Stage 1 (OCR) fails → retry 3× with exponential backoff. Stage 2 (LLM extraction) fails → retry once (LLM APIs are occasionally flaky), then route to human review. Don't retry human review routing — if classification fails, always default to human review rather than auto-approving.

---

## Cross-Questions

**How do you handle documents in different languages?**

Language detection as the first step (langdetect library or FastText language classifier, 1ms per document). Route to language-specific NER models (spaCy has models for 60+ languages). For OCR, Tesseract supports 100+ languages — specify language code for better accuracy. For LLM extraction, most modern LLMs handle multilingual input well. Classification models need to be trained on multilingual data. If a language is unsupported, flag for human review.

**How do you handle documents with sensitive PII (Social Security Numbers, passport numbers)?**

PII detection before storage. After text extraction, run a PII scanner (AWS Comprehend, Microsoft Presidio, or custom regex patterns) that identifies SSN, credit card numbers, passport numbers, medical record numbers. Options: redact (replace with `[REDACTED]`), encrypt with a separate key, or store in a separate high-security data store with stricter access control. The original document on S3 can be encrypted with customer-managed keys (SSE-KMS). Extraction results stored in PostgreSQL should have PII masked in the JSON field. Maintain an audit log of who accessed PII-containing documents.

**How do you maintain extraction quality over time as document formats change?**

Monitor extraction confidence scores over time. A sudden drop in average confidence for a document type signals format drift — maybe the vendor changed their invoice template. Set up alerting: if average confidence for 'invoice' documents drops below 0.80 over a rolling 7-day window, trigger an alert. The human review queue is the feedback mechanism — reviewers correct extractions. Store corrections in a training dataset. Re-train the extraction model monthly on accumulated corrections. This is a continuous learning loop: model → predictions → corrections → re-training.

**How would you implement parallel stage processing?**

Some stages can run in parallel. For a contract document: classification (what type of document) and entity extraction (who are the parties) are independent — run both simultaneously. Use a fan-out pattern from the orchestrator:

```
Pre-processing completes → publish to two queues simultaneously:
  Queue A: classification workers
  Queue B: extraction workers

Both run in parallel → each publishes results to "merge" queue
Merge worker waits for both results → combines → routes
```

This reduces total processing time significantly — if classification takes 1 second and extraction takes 3 seconds, running in parallel takes 3 seconds instead of 4.

**How do you build the human review interface?**

A web dashboard where reviewers see documents in the review queue. For each document: show the original document (rendered PDF or image), the extracted fields with confidence scores highlighted (low confidence in red), and editable fields to correct values. Reviewer submits corrections → stored back to the extracted_data JSON. Reviewers are assigned documents based on their domain expertise (legal reviewer for contracts, finance reviewer for invoices). Track reviewer accuracy over time — compare their corrections against ground truth on test documents. High reviewer accuracy = reliable ground truth for model retraining.
