# Q12: Design Document Processing Pipeline

---

## How to Approach This in an Interview

Document processing combines computer vision (OCR), NLP (extraction, classification), and distributed pipeline design. The interesting architectural challenge is the state machine: a document moves through stages, each stage can fail independently, and you need visibility into exactly where it is. Start with the pipeline stages and the state machine — that's what differentiates a solid answer.

---

## Clarifying Questions

**1. What document types?**

"PDFs, scanned images, Word files? Or all of the above?"

*Why this matters:* Machine-readable PDFs (text-based) just need text extraction. Scanned images need OCR first. Word files need DOCX parsing. Each requires different preprocessing.

**2. What's the processing goal?**

"Are we extracting structured data from documents (invoice → line items), classifying document types, or doing both?"

*Why this matters:* Classification needs an ML model. Extraction needs NER or LLM-based extraction. Both together is a multi-stage pipeline.

**3. Volume and latency?**

"How many documents per day, and how quickly must they be processed after upload?"

*Why this matters:* 100 docs/day = simple sequential pipeline. 500K/day = distributed parallel workers with auto-scaling.

**4. Human review?**

"For low-confidence extractions, should a human verify the results, or is fully automated processing required?"

*Why this matters:* Human review needs a review dashboard, assignment system, correction storage, and feedback loop for model retraining.

### Assumptions

```
- Mixed types: PDFs (machine-readable + scanned), Word, images
- Goal: OCR → extraction (entities, key-value pairs) → classification → structured output
- 500K documents/day = ~5.8 docs/sec average, bursts to 50 docs/sec
- Processing SLA: 5 minutes from upload to processed result
- Human review for low-confidence (< 85%) extractions
- Each document gets a confidence score; documents below threshold go to human review
```

---

## Back-of-Envelope Math

```
Volume: 500K docs/day = 5.8 docs/sec average

If 30% are scanned (need OCR):
  150K docs/day × Textract: $0.015/page × 10 pages avg = $22,500/day
  → Budget for OCR: evaluate Tesseract vs Textract per document value

Processing time targets:
  Pre-processing (parse): 1-5 seconds
  OCR (if needed): 10-30 seconds
  Extraction: 1-5 seconds (NER) or 10-30 seconds (LLM-based)
  Classification: 0.5 seconds
  Total: 12-60 seconds per document
  
  Parallelism needed for 5-minute SLA:
  60 seconds per doc, 500K/day = 5.8 docs/sec needed
  With 30 workers: 30 × (1/60 docs/sec) = 0.5 docs/sec each → 30 workers needed
```

---

## High Level Design

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                    DOCUMENT PROCESSING PIPELINE                              │
│                                                                              │
│  Upload ──▶ S3 ──▶ SQS ──▶ ┌───────────────────────────────────────────┐  │
│                              │         Stage 1: Pre-processing           │  │
│                              │  Type detection (magic bytes)             │  │
│                              │  PDF text extraction (PyMuPDF)            │  │
│                              │  Scanned PDF → OCR queue                  │  │
│                              └─────────────────┬─────────────────────────┘  │
│                                                 │ (clean text)               │
│                                                 ▼                            │
│                              ┌───────────────────────────────────────────┐  │
│                              │       Stage 2: Information Extraction     │  │
│                              │  Named Entity Recognition (spaCy/BERT)   │  │
│                              │  Key-value extraction (forms)             │  │
│                              │  LLM extraction (complex documents)       │  │
│                              │  Confidence scoring per field             │  │
│                              └─────────────────┬─────────────────────────┘  │
│                                                 │ (JSON)                     │
│                                                 ▼                            │
│                              ┌───────────────────────────────────────────┐  │
│                              │       Stage 3: Classification & Routing   │  │
│                              │  Document type: invoice/contract/form     │  │
│                              │  Overall confidence score                  │  │
│                              │  Route: auto-approve OR human review       │  │
│                              └─────────────────┬─────────────────────────┘  │
│                                                 │                            │
│                              ┌──────────────────┴───────────────┐           │
│                              ▼                                   ▼           │
│                    ┌──────────────────┐             ┌────────────────────┐  │
│                    │  Output Store    │             │  Human Review Queue│  │
│                    │  (PostgreSQL +   │             │  (Review Dashboard)│  │
│                    │   S3)            │             └────────────────────┘  │
│                    └──────────────────┘                                      │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Why SQS between each stage?**

Each stage is a separate worker pool. SQS decouples them — if OCR is slow, pre-processing workers can finish their work and publish to SQS without waiting. OCR workers drain the queue at their own pace.

If you connect stages directly (Stage 1 calls Stage 2 synchronously), one slow stage blocks everything. With SQS, each stage scales independently based on its queue depth.

---

## Part 1: Pre-processing Stage

### Document Type Detection

Never trust file extensions — they can be wrong or spoofed. Use "magic bytes" — the first few bytes of a file that identify its format:

```python
def detect_type(content_bytes: bytes) -> str:
    """
    Magic byte signatures (first few bytes of file):
    PDF:  bytes 0-3 = b'%PDF' (ASCII: percent, P, D, F)
    JPEG: bytes 0-1 = b'\xff\xd8'
    PNG:  bytes 0-7 = b'\x89PNG\r\n\x1a\n'
    DOCX: bytes 0-3 = b'PK\x03\x04' (DOCX is a ZIP archive)
    BMP:  bytes 0-1 = b'BM'
    """
    signatures = {
        b'%PDF': 'pdf',
        b'\xff\xd8': 'jpeg',
        b'\x89PNG': 'png',
        b'PK\x03\x04': 'docx_or_xlsx',  # need further inspection
        b'BM': 'bmp',
        b'GIF8': 'gif'
    }
    
    for magic, file_type in signatures.items():
        if content_bytes[:len(magic)] == magic:
            return file_type
    
    return 'unknown'
```

### PDF Processing

```python
import fitz  # PyMuPDF

def extract_pdf_text(pdf_bytes: bytes) -> tuple[str, bool]:
    """Returns (text, is_scanned)"""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    full_text = ""
    
    for page_num in range(doc.page_count):
        page = doc[page_num]
        page_text = page.get_text("text")  # extract embedded text
        full_text += page_text
    
    # Is this a scanned PDF? 
    # Scanned PDFs have pages but no embedded text (or very little)
    avg_chars_per_page = len(full_text) / doc.page_count if doc.page_count > 0 else 0
    is_scanned = avg_chars_per_page < 50  # threshold: < 50 chars/page = likely scanned
    
    return full_text, is_scanned
```

### OCR for Scanned Documents

**What is OCR (Optical Character Recognition)?**

OCR converts images of text into machine-readable text. It works by:
1. Detecting regions that contain text (text detection)
2. Recognizing individual characters in those regions (character recognition)
3. Assembling characters into words and lines

**Two options:**

**Tesseract (open source):**
- Free, runs locally
- Accuracy: 85-95% for clean scans, degrades on poor quality
- Speed: 1-5 seconds per page
- Use for: high-volume low-value documents where cost matters

**AWS Textract (managed service):**
- ~99% accuracy for standard printed text
- Handles tables, forms, multi-column layouts natively
- Price: $0.015 per page (expensive at scale)
- Returns structured form data (key-value pairs in forms): "Name: John Smith" → `{key: "Name", value: "John Smith"}`
- Use for: high-value documents (legal, financial, medical) where accuracy matters

```python
def ocr_with_textract(image_bytes: bytes) -> dict:
    import boto3
    textract = boto3.client('textract')
    
    # FeatureTypes=['TABLES', 'FORMS'] enables structured extraction
    response = textract.analyze_document(
        Document={'Bytes': image_bytes},
        FeatureTypes=['TABLES', 'FORMS']
    )
    
    # Extract plain text (line by line)
    text_lines = [
        block['Text'] 
        for block in response['Blocks'] 
        if block['BlockType'] == 'LINE'
    ]
    full_text = '\n'.join(text_lines)
    
    # Extract form key-value pairs
    # Example: "Invoice Date" → "June 22, 2026"
    kv_pairs = extract_key_value_pairs(response['Blocks'])
    
    # Extract table data (structured grid)
    tables = extract_tables(response['Blocks'])
    
    return {
        'text': full_text,
        'kv_pairs': kv_pairs,   # {"Invoice Date": "June 22, 2026", "Total": "$1,250"}
        'tables': tables         # [[row1_col1, row1_col2], [row2_col1, ...]]
    }
```

**Why image pre-processing matters:**

OCR accuracy degrades with:
- Skew (tilted scan): correct with rotation detection
- Low contrast: binarize (convert to pure black-and-white)
- Low DPI: below 300 DPI, character recognition fails. Upscale to 300 DPI minimum.
- Noise (scanner artifacts): remove with noise reduction filters

```python
from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

def preprocess_for_ocr(image: Image.Image) -> Image.Image:
    # Step 1: Convert to grayscale
    gray = image.convert('L')
    
    # Step 2: Increase contrast
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.0)
    
    # Step 3: Binarize (Otsu's threshold)
    arr = np.array(gray)
    threshold = np.mean(arr)
    binary = Image.fromarray((arr > threshold).astype(np.uint8) * 255)
    
    # Step 4: Ensure 300 DPI
    width, height = binary.size
    target_width = int(width * 300 / 72)  # assuming 72 DPI input
    binary = binary.resize((target_width, int(height * target_width / width)), 
                           Image.LANCZOS)
    
    return binary
```

---

## Part 2: Information Extraction Stage

### Named Entity Recognition (NER)

```python
import spacy

nlp = spacy.load("en_core_web_lg")

def extract_named_entities(text: str) -> dict:
    """
    spaCy entity labels:
    PERSON: "John Smith", "Dr. Adams"
    ORG:    "Acme Corp", "Google LLC"
    DATE:   "June 22, 2026", "next Monday"
    MONEY:  "$1,250.00", "€500"
    GPE:    geographic/political entity: "New York", "India"
    LAW:    "Section 12(b)", "HIPAA"
    """
    doc = nlp(text)
    
    entities = {
        'persons': [],
        'organizations': [],
        'dates': [],
        'amounts': [],
        'locations': [],
        'legal_references': []
    }
    
    label_map = {
        'PERSON': 'persons',
        'ORG': 'organizations',
        'DATE': 'dates',
        'MONEY': 'amounts',
        'GPE': 'locations',
        'LAW': 'legal_references'
    }
    
    for ent in doc.ents:
        if ent.label_ in label_map:
            entities[label_map[ent.label_]].append(ent.text)
    
    return entities
```

**Why the generic NER model isn't enough for specialized domains:**

spaCy's "en_core_web_lg" is trained on Wikipedia and news text. It recognizes "Force Majeure" as an organization (because it looks like a proper noun), not as a legal clause type. "LIBOR rate" might not be recognized as a financial term.

For domain-specific documents: fine-tune a BERT model on labeled examples from your domain. 1,000 labeled documents is usually enough to significantly improve domain-specific extraction.

### LLM-based Extraction for Complex Documents

```python
def extract_with_llm(text: str, document_type: str) -> dict:
    """Use LLM for complex, free-form extraction."""
    
    # Template varies by document type
    if document_type == "contract":
        fields = ["contract_date", "parties", "payment_terms", 
                  "termination_clause", "penalty_clauses", "governing_law"]
    elif document_type == "invoice":
        fields = ["invoice_number", "invoice_date", "vendor_name", 
                  "total_amount", "tax_amount", "due_date", "line_items"]
    
    prompt = f"""Extract the following fields from this {document_type}.
Return a JSON object only, no explanation.
Fields to extract: {', '.join(fields)}
If a field is not found, return null for that field.

Document text (first 4000 chars):
{text[:4000]}

JSON:"""
    
    response = llm.complete(prompt, max_tokens=500, temperature=0)
    
    try:
        extracted = json.loads(response)
    except json.JSONDecodeError:
        # LLM didn't return valid JSON — retry with stricter prompt
        extracted = {}
    
    return extracted
```

**Cost analysis:**

NER (spaCy): free, < 100ms per document.
LLM extraction (GPT-4): ~$0.05 per document.

Strategy: Use NER for all documents (cheap, fast baseline). Use LLM only for high-value documents (contracts, legal agreements) or when NER confidence is low.

### Confidence Scoring

```python
def score_field_confidence(field_name: str, extracted_value: str, 
                           raw_text: str) -> float:
    """
    Score confidence that the extracted value is correct.
    """
    if extracted_value is None:
        return 0.0
    
    # Exact string present in document → high confidence
    if extracted_value in raw_text:
        return 0.95
    
    # Fuzzy match → medium confidence
    from difflib import SequenceMatcher
    best_ratio = max(
        SequenceMatcher(None, extracted_value, segment).ratio()
        for segment in [raw_text[i:i+len(extracted_value)+20] 
                       for i in range(0, min(len(raw_text), 5000), 50)]
    )
    
    if best_ratio > 0.85:
        return 0.75  # close match
    elif best_ratio > 0.70:
        return 0.55
    else:
        return 0.30  # couldn't verify
```

---

## Part 3: Classification and Routing

```python
from transformers import pipeline

# Fine-tuned BERT classifier (trained on labeled documents from your domain)
classifier = pipeline("text-classification", 
                      model="your-org/document-classifier",
                      return_all_scores=True)

def classify_document(text: str) -> tuple[str, float]:
    """Returns (document_type, confidence)"""
    
    # Use first 512 tokens (BERT's limit)
    truncated_text = ' '.join(text.split()[:400])
    
    results = classifier(truncated_text)
    
    # results: [{"label": "invoice", "score": 0.87}, 
    #            {"label": "contract", "score": 0.08}, ...]
    best = max(results[0], key=lambda x: x['score'])
    
    return best['label'], best['score']

def route_document(doc_id: str, classification_confidence: float,
                   extracted_fields: dict) -> str:
    """Decide: auto-approve or send to human review."""
    
    AUTO_APPROVE_THRESHOLD = 0.85
    HUMAN_REVIEW_THRESHOLD = 0.60
    
    # Check overall classification confidence
    if classification_confidence < HUMAN_REVIEW_THRESHOLD:
        return "human_review"  # document type uncertain
    
    # Check field-level confidence
    low_confidence_fields = [
        field for field, data in extracted_fields.items()
        if isinstance(data, dict) and data.get('confidence', 1.0) < 0.70
    ]
    
    if len(low_confidence_fields) > 2:
        return "human_review"  # too many uncertain fields
    
    if classification_confidence >= AUTO_APPROVE_THRESHOLD and len(low_confidence_fields) == 0:
        return "auto_approve"
    
    return "human_review"  # middle ground: let humans decide
```

---

## Document State Machine

Every document has a `status` field that tracks its current position in the pipeline:

```
uploaded ──▶ preprocessing ──▶ extracting ──▶ classifying ──▶ auto_approved
                                                                    OR
                                                              pending_review ──▶ reviewed
                                                                    OR
                                ──▶ failed (at any stage)
```

```sql
CREATE TABLE documents (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         BIGINT       NOT NULL,
    filename        VARCHAR(500) NOT NULL,
    s3_key          VARCHAR(1000) NOT NULL,        -- where raw file lives
    file_type       VARCHAR(50),                   -- 'pdf', 'jpeg', 'docx'
    
    status          ENUM(
        'uploaded',          -- just arrived, not yet processed
        'preprocessing',     -- Stage 1 running
        'extracting',        -- Stage 2 running
        'classifying',       -- Stage 3 running
        'auto_approved',     -- high confidence, done
        'pending_review',    -- needs human review
        'reviewed',          -- human reviewed and approved
        'failed'             -- unrecoverable error
    ) DEFAULT 'uploaded',
    
    document_type   VARCHAR(100),                  -- 'invoice', 'contract', ...
    confidence      DECIMAL(4,3),                  -- overall confidence 0.000-1.000
    extracted_data  JSON,                          -- structured extraction result
    error_message   TEXT,
    
    -- Timing for SLA monitoring
    processing_started_at    DATETIME,
    processing_completed_at  DATETIME,
    
    created_at      DATETIME NOT NULL DEFAULT NOW(),
    
    INDEX idx_user_status (user_id, status),
    INDEX idx_status_created (status, created_at)
);

CREATE TABLE processing_events (
    id           BIGINT PRIMARY KEY AUTO_INCREMENT,
    document_id  UUID NOT NULL,
    stage        VARCHAR(100) NOT NULL,          -- 'preprocessing', 'ocr', 'extraction'
    status       ENUM('started', 'completed', 'failed') NOT NULL,
    duration_ms  INT,
    error        TEXT,
    created_at   DATETIME NOT NULL,
    INDEX idx_document_id (document_id)
);
-- Full audit trail: every stage transition logged
-- Query: SELECT * FROM processing_events WHERE document_id = X
-- Shows exactly when each stage started, completed, how long it took
```

---

## Scale — What Breaks at 10x?

10x = 5M documents/day = 58 docs/sec average.

**OCR throughput:**

AWS Textract has concurrency limits. Use SQS to queue documents for OCR, scale Textract caller workers based on queue depth. Each Textract call takes 10-30 seconds. At 58 scanned docs/sec (assuming 30% are scanned = 17 docs/sec), with 30-second processing time, need 510 concurrent Textract calls.

Cost: 5M docs/day × 30% scanned × 10 pages × $0.015/page = $225,000/day. Prohibitive. Switch to: Tesseract for bulk (cheap, 85% accuracy), Textract only for documents flagged as high-value.

**LLM extraction cost:**

At $0.05/document and 5M/day = $250,000/day. Not sustainable.

Solutions:
1. Use LLM only for complex documents (contracts, legal) — maybe 10% of volume → $25K/day
2. Fine-tune a smaller model (Llama 3 8B) on your extracted data → one-time $10K training, $0.001/doc inference
3. Rule-based extraction for well-structured documents (invoices with consistent templates) → nearly free

**Workers:** Each stage is a separate Kubernetes Deployment. Auto-scale based on SQS queue depth. OCR workers might need 500 replicas during peak. Extraction workers might need 50 replicas. Each scales independently — Textract I/O bound vs extraction CPU bound.

---

## Trade-offs

**Rule-based vs ML extraction:**

Rules: fast, cheap, deterministic, easy to debug. Break on format variation (invoice from vendor A vs vendor B look different).

ML: handles variation, generalizes across formats. Black box, requires labeled training data, drifts as document formats change. Requires quarterly retraining.

**Hybrid strategy:** Use rule-based for documents with known, fixed formats (your company's own form templates). Use ML/LLM for varied external documents (third-party invoices, partner contracts).

**Asynchronous pipeline vs synchronous:**

Synchronous (user waits for 5-minute processing): bad UX. Forces users to sit idle.

Asynchronous (return job ID immediately, notify when complete): correct for this use case. Webhook notification or polling for status. Users start other work while documents process.

---

## Cross-Questions

**Q: How do you handle multi-page documents where information spans pages?**

```python
# Context-aware chunking: process the full document, not page by page
# Important: page breaks in a PDF don't mean semantic breaks

# When extracting "payment terms" from a contract:
# The relevant text might start on page 3 and continue on page 4
# → Process the full concatenated text, not individual pages

full_text = ""
for page in document.pages:
    full_text += page.text + " "  # concatenate, let NLP handle sentence boundaries

# For LLM extraction: the full document might exceed context window
# Split into overlapping sections, extract from each, merge:
def extract_from_large_document(text: str, fields: list[str]) -> dict:
    SECTION_SIZE = 3000  # tokens
    OVERLAP = 500        # tokens of overlap between sections
    
    words = text.split()
    results = {}
    
    for i in range(0, len(words), SECTION_SIZE - OVERLAP):
        section = ' '.join(words[i:i + SECTION_SIZE])
        section_result = extract_with_llm(section, fields)
        
        # Merge: prefer non-null values, higher confidence wins
        for field, value in section_result.items():
            if value is not None and (field not in results or results[field] is None):
                results[field] = value
    
    return results
```

**Q: How do you maintain extraction quality over time as document formats change?**

1. **Monitor confidence scores over time:** If average confidence for "invoice" documents drops from 0.87 to 0.74 over 2 weeks, something changed.

2. **Feedback loop from human review:** When reviewers correct an extraction, store the correction:
   ```
   { document_id: X, field: "total_amount", 
     extracted: "$1,250", 
     corrected: "$12,500",   ← reviewer caught a decimal error
     reviewer_id: 123 }
   ```

3. **Monthly retraining:** Accumulate 500+ corrections → retrain extraction model on original + corrections. Model adapts to format drift.

4. **A/B test new models:** Before deploying a retrained model, test on held-out validation set. Only deploy if metrics improve.

**Q: How would you build the human review interface?**

```
Review Dashboard:
  ┌─────────────────────────────────────────────────────┐
  │  Document: invoice_2026_june_vendor_abc.pdf          │
  │  Status: Pending Review (Confidence: 71%)            │
  ├─────────────────────────────────────────────────────┤
  │  ┌─────────────────┐  ┌──────────────────────────┐  │
  │  │   Document      │  │   Extracted Fields        │  │
  │  │   (rendered     │  │                           │  │
  │  │    PDF viewer)  │  │   Invoice Date: 06/22/26 ✓│  │
  │  │                 │  │   ← HIGH CONFIDENCE (95%) │  │
  │  │                 │  │                           │  │
  │  │  [highlighted:  │  │   Total Amount: $1,250 ⚠  │  │
  │  │   "Total:       │  │   ← LOW CONFIDENCE (55%)  │  │
  │  │    $1,250.00"]  │  │   [editable field: _____ ]│  │
  │  │                 │  │                           │  │
  │  │                 │  │   Vendor Name: Acme Corp ✓│  │
  │  │                 │  │   ← HIGH CONFIDENCE (92%) │  │
  │  └─────────────────┘  └──────────────────────────┘  │
  │  [APPROVE]  [REJECT]  [SKIP TO NEXT]                 │
  └─────────────────────────────────────────────────────┘
```

Low-confidence fields are highlighted in red/amber, pre-populated with the extracted value, and editable. Reviewer focuses attention on uncertain fields, confirming or correcting. High-confidence fields show as read-only with green checkmark.

Queue assignment: route legal documents to legal reviewers, financial documents to finance team. Track reviewer accuracy by comparing their corrections against ground-truth test documents. High-accuracy reviewers handle complex documents; new reviewers get standard ones.
