# Q7: Design File Upload System (S3-like)

---

> **Interview Phase Map** → Phase 1: Requirements (5 min) · Phase 2: Core Entities (2 min) · Phase 3: API Design (5 min) · Phase 4: High Level Design (12 min) · Phase 5: Deep Dives (10 min)

---

## Introduction

A file upload system allows users to store, retrieve, and manage files — images, videos, documents, backups — reliably in the cloud. Amazon S3, Google Cloud Storage, and Dropbox are the most well-known examples. The system must handle files ranging from a few kilobytes to several gigabytes, serve them to potentially millions of concurrent users, and guarantee that once a file is uploaded it is never lost.

The fundamental challenge is that files are not like database rows. They are large binary blobs that cannot be efficiently stored or queried in a relational database. Instead, they are stored in object storage — flat key-value systems optimized for storing and retrieving large binary objects. The file is stored with a unique key (often a hash of the content or a UUID), and metadata about it (name, owner, size, content type) is stored separately in a database.

Large file uploads introduce their own problems. Uploading a 2GB video as a single HTTP request is fragile — if the connection drops halfway through, the entire upload must restart. The standard solution is **multipart upload**: the client splits the file into smaller chunks (e.g., 5MB each), uploads each chunk independently, and the server reassembles them once all parts arrive. This makes uploads resumable and parallelizable.

Reliability and durability are non-negotiable. Files must survive hardware failures, data center outages, and disk corruption. This is achieved through replication — storing multiple copies of each file across different physical locations. S3, for example, guarantees 99.999999999% durability by replicating data across multiple availability zones within a region.

Access control, CDN integration for fast global delivery, versioning (keeping older versions of a file), and lifecycle policies (automatically deleting or archiving old files) are commonly expected in a complete design discussion.

---

## How to Approach This in an Interview

The key insight in file upload design is the **pre-signed URL pattern**: for any non-trivial file, your application servers should never touch the actual bytes. The client uploads directly to S3. Your servers only handle metadata. This keeps your application servers cheap and fast. Make sure you explain this clearly — it's the most important concept in this design.

---

## Clarifying Questions

**1. File size range?**

"Are we handling small files like profile pictures (<1MB) or large files like videos (multi-GB)? Large files require chunked multipart upload."

*Why this matters:* A 4GB video can't be sent in one HTTP request reliably — network drops mean restarting from zero. Chunked upload allows resuming from the last successful chunk.

**2. Who are the users?**

"Is this a product feature (users uploading photos to their profile) or a developer platform (S3-like API for other services to store files)?"

*Why this matters:* Product feature = simple upload button, specific use cases. Developer platform = generic API, IAM-style access control, SDKs.

**3. Access control?**

"Are files public (anyone can download) or private (only owner can download)? Do we need signed download URLs that expire?"

*Why this matters:* Private files need signed URLs for every download — you can't put the S3 URL in the browser directly. Signed URLs have expiry times and cryptographic signatures.

**4. Durability requirements?**

"Do we need S3-level 11 nines durability (multi-AZ replication) or is single-zone acceptable?"

*Why this matters:* Multi-AZ replication = 3 copies of every file in different data centers. Higher cost, much higher durability.

### Assumptions

```
- Files from 1KB (thumbnails) to 5GB (videos)
- Both small (< 100MB, single-request) and large (multipart chunked) uploads
- Mix of public and private files
- Signed URLs for private file access (15-minute expiry)
- High durability (3x replication across availability zones)
- 50M DAU, 10M file uploads/day = 115 uploads/sec
- Average file size: 10MB → 1.15 GB/sec upload throughput
- Downloads 10x uploads → CDN handles most of this
```

---

## Functional Requirements

- Users should be able to upload files of any type up to 5GB and receive a stable access URL
- Users should be able to download files via direct URL (public) or time-limited signed URL (private)
- Users should be able to delete files they own

> **How to say this in the interview:** *"I see three core things users need — upload files up to 5GB and receive a stable access URL, download them either directly if public or via a time-limited signed URL if private, and delete files they own. Does that capture it?"* The signed URL detail is worth stating explicitly upfront because it implies a meaningful security design choice — better to get alignment on it now than after you've built the architecture.

## Non-functional Requirements

> **NFR = Non-Functional Requirements.** These answer *how the system behaves*, not *what it does*. FR = "users should be able to post a tweet" (the feature). NFR = "the feed must load in under 200ms" (the quality). Same system, completely different axis.

- **High durability (99.999999%)**: files must not be lost — 3x replication across availability zones
- **Resumable uploads**: large file uploads must survive network interruptions without restarting from scratch
- **Download latency < 100ms TTFB**: CDN-served for public files; global edge delivery
- **Scale**: 10M uploads/day ≈ 115/sec; downloads are 10x uploads — CDN absorbs the majority
- **Availability over Consistency**: metadata staleness is acceptable; upload/download path must always be available

> **How to say this in the interview:** After agreeing on FRs, transition with: *"Now let me think about the non-functional requirements — the qualities the system needs to have, not just the features."* Then state each of the points listed above with its specific number or reason attached. Always quantify — "the system should be fast" signals nothing; the specific path and millisecond target is what shows you understand the system. Close with: *"Any specific constraints I should factor into my design?"*
>
> **Mental checklist for any system — pick your top 3:** Run through these mentally every time: *Is stale data acceptable, or must it always be correct?* (CAP — AP or CP?), *Which specific path must be fastest, and what is the millisecond target?* (Latency), *What is the read-to-write ratio and peak QPS?* (Scale). Add Durability, Security, or Compliance only when they are the defining constraint for that particular system — do not list all eight just to look thorough.

---

## Back-of-Envelope Math

> **Interview note:** Skip this section out loud. Say: *"I'll skip capacity estimation upfront — I'll do the math only if a specific number would directly change a design decision."* Then move on. The calculations above are study material — they show you the scale of this system and tell you what to optimize for.

```
Uploads: 10M/day = 115/sec
Average file: 10MB
Upload bandwidth: 115 × 10MB = 1.15 GB/sec

Downloads: 10x uploads = 11.5 GB/sec
  CDN serves ~90% → ~1.15 GB/sec hits origin S3
  S3 can handle this easily

Storage:
  10M files/day × 10MB = 100 TB/day
  100 TB/day × 365 days = 36.5 PB/year
  With 3x replication = 109.5 PB/year of raw storage
  → Use S3 Intelligent Tiering: hot files on SSD, cold files on S3 Glacier

Metadata DB:
  10M files/day × 500 bytes/record = 5 GB/day of metadata
  MySQL handles this with monthly partitioning
```

---

## Core Entities

- **User** — identity + storage quota
- **File** — metadata: name, size, MIME type, visibility (public/private), owner, checksum
- **Chunk** — part of an in-progress multipart upload (ephemeral until completed)
- **SignedURL** — pre-signed access token with expiry for private file downloads

> **How to say this in the interview:** *"Before I draw anything, let me get the core data entities on the board."* Then list them by name with a one-liner each. Close with: *"I'll keep the schema intentionally light right now — I'll add the relevant columns directly next to the database component as we go through each endpoint."* This signals good design instincts: you know that the schema emerges from the design, not the other way around.
>
> **What not to do:** Do not write out full table schemas with every column at this stage. The interviewer already knows a User table has a name, email, and password hash — writing those wastes time and signals you don't know what to prioritize. Save schema columns for the High Level Design phase, where you add them next to the relevant database in the diagram.

---

## API Design

> **Why REST (with a key variation for large files):** REST handles the metadata and control operations cleanly. The interesting design decision is for large file uploads — rather than streaming 5GB through our servers, the client receives pre-signed S3 URLs and uploads each part directly to S3. This bypasses our application servers entirely, which is both cheaper and faster. Say: *"I'll use REST for the API. The important design decision is that for large files, I won't route bytes through our servers — the client gets pre-signed S3 URLs and uploads parts directly to S3. Our API is just the orchestration layer: initiate the upload, get the URLs, confirm completion. This keeps our servers out of the data path entirely."*

```
// Small files (< 100MB) — single upload
POST /v1/files
body: multipart/form-data { file, visibility: "public|private" }
→ 201: { "file_id": string, "url": string }

// Large files — multipart initiation
POST /v1/uploads
body: { "filename": string, "size": int, "total_parts": int, "visibility": string }
→ 201: { "upload_id": string, "part_urls": string[] }   ← pre-signed S3 URL per part

PUT /v1/uploads/{upload_id}/complete
body: { "parts": [{ "part_number": int, "etag": string }] }
→ 200: { "file_id": string, "url": string }

GET /v1/files/{file_id}/signed-url?expires_in=900
→ 200: { "signed_url": string, "expires_at": timestamp }

DELETE /v1/files/{file_id}
→ 204 No Content
```

---

## High Level Design

> **How to build this diagram in the interview — this phase matters most:** Do not draw the complete architecture upfront. Start by saying: *"Let me build the architecture by going through each endpoint one at a time."* For each endpoint: draw only the components it needs, talk through the data flow out loud as you draw — the interviewer needs to follow your reasoning, not just see boxes appearing — and add the relevant schema fields directly next to the database component in the diagram. When you spot a need for a cache, queue, or additional component mid-drawing, say *"I can see we'll need a cache here — I'm going to note that and come back to it in deep dives"*, then keep moving. Do not solve deep dive problems during this phase. Finish High Level Design only when all three functional requirements have a working data path through the diagram. The diagram above is your reference for what the final state looks like.

```
                                              ┌─────────────────────────────┐
                                              │         S3 Storage          │
                                              │                             │
┌──────────┐                                  │  Bucket: user-uploads       │
│  Client  │──Small file──────▶ Upload API ──▶│  Keys: {user_id}/{file_id}  │
│          │                                  │                             │
│          │──Request presigned URL──▶ API ──▶│  ← Pre-signed PUT URL       │
│          │◀──presigned_url────────────────  │    Client uploads DIRECTLY  │
│          │──PUT directly to S3──────────────│    (bypasses our servers)   │
└──────────┘                                  └──────────┬──────────────────┘
      │                                                   │ S3 Event Notification
      │ download                                          ▼
      │                                         ┌──────────────────┐
      │◀─── CDN ────────────────────────────────│ Upload Processor │
      │     (serves cached files)               │ (virus scan,      │
      │                                         │  thumbnails)      │
      │                                         └──────────────────┘
      │
      ▼
┌──────────────────────────────────────────────┐
│              Metadata Service                 │
│  MySQL: file_id, user_id, size, checksum,     │
│         storage_path, status, is_public       │
└──────────────────────────────────────────────┘
```

**The pre-signed URL pattern — the most important concept:**

Without pre-signed URLs:
```
Client → Upload Server → S3
Upload Server receives ALL the bytes, then forwards to S3.
At 1.15 GB/sec total uploads, your Upload Servers need 1.15 GB/sec bandwidth.
Every uploaded byte touches your servers twice (receive + forward).
```

With pre-signed URLs:
```
Client → Metadata Server (just registers intent, no bytes)
Metadata Server → generates pre-signed S3 URL (contains auth signature)
Client → uploads directly to S3 (your servers see zero bytes)
S3 → fires event notification when upload completes
Event notification → Metadata Server marks file as complete
```

Your servers handle ~100 bytes per upload (metadata), not 10MB. 100,000x less bandwidth.

---

## Part 1: Small File Upload (< 100MB)

For small files, a direct upload through your server is acceptable — it's simpler and faster for the client.

```
Client:
  POST /v1/files
  Headers: Content-Type: image/jpeg, Content-Length: 5242880
  Body: (binary bytes of the file)

Server:
  Step 1: Validate
    - Is Content-Type allowed? (reject executable types)
    - Is Content-Length within quota?
    - Is user within their storage quota?
  
  Step 2: Generate file_id
    file_id = generate_uuid()  # or Snowflake for sortability
  
  Step 3: Compute checksum as bytes arrive
    sha256_hasher = hashlib.sha256()
    while chunk := request.stream.read(65536):  # read in 64KB chunks
        sha256_hasher.update(chunk)
        s3_buffer.write(chunk)
    checksum = sha256_hasher.hexdigest()
  
  Step 4: Upload to S3
    s3.put_object(
        Bucket="user-uploads",
        Key=f"{user_id}/{file_id}",
        Body=s3_buffer,
        ContentType=content_type,
        Metadata={"checksum": checksum}
    )
  
  Step 5: Save metadata to MySQL
    INSERT INTO files (file_id, user_id, storage_key, size_bytes, checksum, 
                       content_type, status, is_public)
    VALUES (file_id, user_id, f"{user_id}/{file_id}", size, checksum, 
            content_type, 'complete', false)
  
  Step 6: Return to client
    { "file_id": "f_abc123", "url": "https://cdn.example.com/f_abc123" }
```

**Why compute checksum on the fly (not after upload)?**

If you compute checksum after upload, you need to read the entire file again from S3 to verify. Computing it as bytes arrive is free — same data, one pass. The checksum detects data corruption during transit (TCP checksum is weak — bit flips can pass it).

---

## Part 2: Large File Upload — Multipart Chunked Upload

For files > 100MB, reliability matters. A 4GB video upload takes several minutes. Any network interruption means restarting from scratch with a single-request upload. Chunked upload allows resuming.

**AWS S3 has native multipart upload support** — we build on top of it.

```
Step 1: Client initiates upload
  POST /v1/uploads/multipart/init
  Body: {
    "filename": "vacation_video.mp4",
    "size": 4294967296,           ← 4GB in bytes
    "content_type": "video/mp4",
    "total_chunks": 410           ← 4GB / 10MB chunks = 410 chunks
  }
  
  Server:
    1. Validate quota (user has 4GB free)
    2. Create multipart upload in S3:
       s3.create_multipart_upload(Bucket="uploads", Key=f"{user_id}/{file_id}")
       → Returns: s3_upload_id = "VXBsb2FkIElE..."
    3. Insert into multipart_uploads table: status='in_progress'
    4. Return:
       {
         "upload_id": "mp_xyz789",
         "s3_upload_id": "VXBsb2FkIElE...",
         "chunk_size": 10485760,   ← 10MB per chunk
         "total_chunks": 410
       }

Step 2: Client uploads each chunk
  Client can parallelize: upload 4 chunks simultaneously for full bandwidth use
  
  PUT /v1/uploads/multipart/{upload_id}/chunks/{chunk_number}
  Body: (10MB binary chunk)
  
  Server:
    1. Receive the chunk bytes
    2. Compute chunk checksum (MD5 — S3 uses MD5 for part ETags)
    3. Upload to S3 as a part:
       s3.upload_part(
           Bucket="uploads",
           Key=f"{user_id}/{file_id}",
           UploadId=s3_upload_id,
           PartNumber=chunk_number,
           Body=chunk_bytes
       )
       → S3 returns: ETag = "abc123..."  (MD5 of this part)
    4. Record in upload_chunks table:
       INSERT INTO upload_chunks (upload_id, chunk_number, etag, uploaded_at)
    5. Return: { "chunk": 1, "etag": "abc123..." }
  
  Parallel uploads:
    Client uploads chunks 1, 2, 3, 4 simultaneously (4 connections)
    At 100 Mbps upload speed, 4 parallel × 10MB = 40MB in parallel
    Upload time: 4GB / 40MB/s = 100 seconds ≈ 1.5 minutes

Step 3: Complete the upload
  POST /v1/uploads/multipart/{upload_id}/complete
  Body: {
    "parts": [
      { "chunk_number": 1, "etag": "abc123..." },
      { "chunk_number": 2, "etag": "def456..." },
      ...
    ]
  }
  
  Server:
    1. Verify all 410 chunks are present in upload_chunks table
    2. Tell S3 to assemble:
       s3.complete_multipart_upload(
           Bucket="uploads",
           Key=f"{user_id}/{file_id}",
           UploadId=s3_upload_id,
           MultipartUpload={"Parts": [{"PartNumber": n, "ETag": etag} for n, etag in parts]}
       )
       S3 assembles all 410 parts into one object atomically
       → Returns: final object ETag (MD5 of MD5s of all parts)
    3. Update files table: status='complete'
    4. Trigger post-processing (virus scan, thumbnails)
    5. Return: { "file_id": "f_abc123", "url": "..." }

Step 4: Resume after interruption
  If connection drops after chunk 200, client needs to know which chunks succeeded.
  
  GET /v1/uploads/multipart/{upload_id}/status
  Server:
    SELECT chunk_number FROM upload_chunks WHERE upload_id = ?
    Returns: { "uploaded_chunks": [1,2,...,200], "missing": [201,...,410] }
  
  Client resumes from chunk 201. No re-uploading of completed chunks.
```

---

## Part 3: Pre-signed URLs for Direct Upload

For large files where you don't want to proxy bytes through your servers:

```python
# Server generates pre-signed URL
import boto3
from datetime import datetime, timedelta

def generate_upload_url(user_id: str, file_id: str, content_type: str) -> str:
    s3 = boto3.client('s3')
    
    # Pre-signed URL: a regular S3 URL with temporary auth embedded
    # The URL contains: Bucket, Key, expiry, and a cryptographic signature
    # Anyone with this URL can PUT an object to this exact S3 path
    # until expiry (1 hour from now)
    
    presigned_url = s3.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': 'user-uploads',
            'Key': f'{user_id}/{file_id}',
            'ContentType': content_type,
        },
        ExpiresIn=3600  # 1 hour validity
    )
    
    # URL looks like:
    # https://user-uploads.s3.amazonaws.com/user123/file456
    # ?X-Amz-Algorithm=AWS4-HMAC-SHA256
    # &X-Amz-Credential=AKIA.../us-east-1/s3/aws4_request
    # &X-Amz-Date=20260622T103000Z
    # &X-Amz-Expires=3600
    # &X-Amz-Signature=abc123...  ← cryptographic proof
    
    return presigned_url

# Client flow:
# 1. GET /v1/files/upload-url?content_type=video/mp4&size=4294967296
# 2. Server: validate quota, INSERT files record (status='uploading'), return presigned_url
# 3. Client: PUT presigned_url (directly to S3, no server involvement)
# 4. S3: file uploaded → fires S3 Event Notification to SQS
# 5. Lambda/Worker: receives SQS event, marks file status='complete'
```

**Security of pre-signed URLs:**

The URL contains a HMAC-SHA256 signature computed using AWS credentials. S3 verifies the signature on every request. If the URL has expired, S3 rejects the PUT. If someone tries to modify the URL (change the Key path), the signature fails. The URL is safe to give to untrusted clients.

---

## Part 4: Signed Download URLs for Private Files

Private files should never have their S3 URL exposed directly. If you put the raw S3 URL in an `<img>` tag, anyone can share that URL and download the file forever.

```python
def get_download_url(user_id: str, file_id: str) -> str:
    # 1. Verify the requesting user owns this file
    file = db.get_file(file_id)
    if file.user_id != user_id:
        raise ForbiddenError("You don't own this file")
    
    if not file.is_active:
        raise NotFoundError("File not found")
    
    # 2. Generate a signed URL valid for 15 minutes
    s3 = boto3.client('s3')
    download_url = s3.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': 'user-uploads',
            'Key': f'{user_id}/{file_id}'
        },
        ExpiresIn=900  # 15 minutes
    )
    
    return download_url

# Client flow:
# GET /v1/files/{file_id}/download
# Server validates auth, returns { "url": "https://s3.amazonaws.com/...?Signature=..." }
# Client redirects to the signed URL
# After 15 minutes, the URL stops working
# Next time: client calls /download again to get a fresh URL
```

**For public files:** Store in a separate S3 bucket with public-read ACL. URL is permanent: `https://cdn.example.com/{file_id}`. Serve via CloudFront CDN. Never expires.

---

## Data Model

```sql
CREATE TABLE files (
    file_id         VARCHAR(36)  PRIMARY KEY,
    -- UUID format: "550e8400-e29b-41d4-a716-446655440000"
    
    user_id         BIGINT       NOT NULL,
    bucket          VARCHAR(100) NOT NULL,    -- S3 bucket name
    storage_key     VARCHAR(500) NOT NULL,    -- S3 object key: "user123/file456"
    filename        VARCHAR(500) NOT NULL,    -- original filename shown to user
    content_type    VARCHAR(100) NOT NULL,    -- "image/jpeg", "video/mp4"
    
    size_bytes      BIGINT       NOT NULL,    -- for quota calculation
    checksum        CHAR(64)     NOT NULL,    -- SHA256 hex string (64 chars)
    -- Used for: integrity verification, deduplication detection
    
    status          ENUM('uploading', 'processing', 'complete', 'deleted')
                    DEFAULT 'uploading',
    -- 'uploading': file not fully received yet
    -- 'processing': virus scan / thumbnails in progress
    -- 'complete': ready to serve
    -- 'deleted': soft deleted (file still on S3 for 30 days)
    
    is_public       BOOLEAN      DEFAULT FALSE,
    -- Public: served via CDN with permanent URL
    -- Private: requires signed download URL
    
    thumbnail_url   VARCHAR(500),            -- generated after upload
    virus_scan_result ENUM('clean', 'infected', 'pending') DEFAULT 'pending',
    
    created_at      DATETIME     NOT NULL DEFAULT NOW(),
    deleted_at      DATETIME,                -- for soft delete
    
    INDEX idx_user_id (user_id),
    INDEX idx_status (status, created_at),
    INDEX idx_checksum (checksum)           -- for deduplication lookups
);

CREATE TABLE multipart_uploads (
    upload_id       VARCHAR(36)  PRIMARY KEY,
    user_id         BIGINT       NOT NULL,
    file_id         VARCHAR(36)  NOT NULL,   -- FK to files
    s3_upload_id    VARCHAR(200) NOT NULL,   -- S3's multipart upload session ID
    filename        VARCHAR(500),
    total_chunks    INT          NOT NULL,
    chunk_size_bytes INT         NOT NULL,
    status          ENUM('in_progress', 'complete', 'aborted') DEFAULT 'in_progress',
    created_at      DATETIME     NOT NULL,
    expires_at      DATETIME     NOT NULL    -- abort stale uploads after 24h
);

CREATE TABLE upload_chunks (
    upload_id       VARCHAR(36)  NOT NULL,
    chunk_number    INT          NOT NULL,   -- 1-indexed
    etag            VARCHAR(64),             -- S3 ETag (MD5 of chunk)
    size_bytes      INT,
    uploaded_at     DATETIME,
    
    PRIMARY KEY (upload_id, chunk_number)
);
```

---

## Post-Upload Processing Pipeline

Every uploaded file goes through processing before being marked 'complete':

```
Upload completes (small file upload or multipart complete)
        │
        ▼
SQS Queue: "files.processing"
        │
        ▼
Processing Worker (runs asynchronously, user doesn't wait):
        │
   ┌────┴─────────────────────────────────────┐
   ▼                                          ▼
Virus Scan                              Thumbnail Generation
(ClamAV or AWS Guardduty)               (if image or video)
        │                                     │
   ┌────┴────┐                          ┌─────┴──────┐
   ▼         ▼                          ▼            ▼
 Clean    Infected                  Success      Failure
   │          │                       │
   ▼          ▼                       ▼
Update     DELETE from           Update files:
files:     S3, notify user       thumbnail_url = s3://thumbs/file_id.jpg
status=    files.status='deleted'
'complete' 
virus=     virus='infected'
'clean'

Total processing time: 5-30 seconds
File shows as 'processing' in UI during this time
Client polls status or receives webhook when complete
```

---

## Scale — What Breaks at 10x?

> **How to transition into deep dives:** Say: *"I now have a working system that satisfies all three functional requirements. Let me harden it by addressing the non-functional requirements I identified at the start."* Then work through the NFRs one by one, starting with the most important. For each one, state the problem it creates in the current design, then your solution. After each point, pause and let the interviewer probe before moving on — do not monologue for more than two minutes at a stretch. The interviewer has specific signals they are looking for; if you are talking, they cannot ask for them. For senior roles, proactively identify the next bottleneck without waiting to be prompted.


10x = 115 uploads/sec → 1,150 uploads/sec, 11.5 GB/sec upload throughput.

**Upload API servers:** For pre-signed URL pattern, servers handle only metadata requests — trivially scalable. For small file uploads proxied through servers, need sufficient bandwidth. At 11.5 GB/sec, deploy on high-bandwidth instances (25 Gbps network). Run 10 upload servers → 2.5 Gbps each.

**S3 throughput:** S3 scales elastically. No bottleneck here. AWS's internal routing handles request distribution across partitions automatically.

**Metadata DB (MySQL):** At 1,150 files/sec, MySQL handles the INSERT easily (1K-5K writes/sec is fine). Download URL generation queries `WHERE file_id = ?` — indexed primary key lookup, sub-millisecond. Add read replicas for download URL generation.

**Virus scanning:** At 1,150 uploads/sec × average 10 second scan = 11,500 concurrent scans. Scale AV workers (AWS Fargate auto-scales based on SQS queue depth). ClamAV or AWS Guardduty Malware Protection for S3.

**Storage costs:** 1,150 uploads/sec × 10MB = 11.5 GB/sec = ~1 PB/day. S3 Intelligent Tiering automatically moves infrequently accessed files to cheaper storage classes (S3-IA, Glacier). Lifecycle policy: move to Glacier after 90 days of inactivity.

---

## Trade-offs

**Chunked multipart vs single request:**

Single request: simpler code, works for small files. Fails on network interruption for large files (restart from zero).

Multipart chunked: complex code (manage chunk state, handle partial uploads). Supports resume, parallel upload (4x faster), per-chunk integrity checks. Always use for files > 100MB.

**Client-side vs server-side checksum:**

Client-side: compute SHA256 on the client before upload, send with the request. Detected corruption before storage costs are incurred. Fast — client already has the data.

Server-side: compute SHA256 as bytes arrive. Catches corruption introduced in transit. More reliable but uses server CPU.

Best practice: both. Client sends checksum, server recomputes and verifies they match. Catches both: client corruption (before send) and transit corruption (after send).

**Deduplication (content-addressable storage):**

If two users upload identical files (same SHA256 checksum), store only one S3 object and create two metadata records pointing to it.

```sql
-- Check if file already exists
SELECT storage_key FROM files WHERE checksum = ? LIMIT 1

-- If found: create metadata record pointing to existing S3 object
-- No S3 upload needed
```

Saves storage costs significantly (profile pictures, common icons). Security risk: if user A sees a near-instant "upload complete" for a file that already exists, they can infer that user B also has that file. For personal files, this is a privacy violation. Never deduplicate across different users' private files — only public/shared content.

---

## Cross-Questions

**Q: How do you handle an upload interrupted at chunk 200 of 410?**

```
Client resumes app after network drop:
  GET /v1/uploads/multipart/{upload_id}/status
  Returns: { "uploaded_chunks": [1..200], "missing": [201..410] }

Client: resume from chunk 201
  PUT /v1/uploads/multipart/{upload_id}/chunks/201 ...
  PUT /v1/uploads/multipart/{upload_id}/chunks/202 ...
  (continue until all done)

Server: S3's multipart upload holds all uploaded parts for 24 hours.
        On complete, S3 assembles all 410 parts into the final object.
        Parts 1-200 are NOT re-uploaded.
```

AWS S3 multipart upload is designed exactly for this — parts are persistent for 24 hours or until the upload is completed or aborted.

**Q: How do you prevent a user from uploading a 1TB file and exceeding their quota?**

```python
def validate_quota(user_id: str, incoming_size: int):
    # Optimistic check (before upload starts)
    user_quota = db.get_quota(user_id)
    # { used_bytes: 15GB, limit_bytes: 20GB }
    
    if user_quota.used_bytes + incoming_size > user_quota.limit_bytes:
        raise QuotaExceededError(
            f"Upload would exceed quota. Used: {used}, Limit: {limit}"
        )
    
    # Reserve the space (optimistic lock)
    db.reserve_quota(user_id, incoming_size)
    # UPDATE user_quota SET reserved_bytes = reserved_bytes + incoming_size

# On upload success: move reserved to used
# On upload failure/abort: release the reservation
```

Background job reconciles `used_bytes` with actual S3 storage daily — eventual consistency is fine for quota. It's okay if a user is slightly over quota for minutes before the reconciliation job catches it.

**Q: How would you generate image thumbnails after upload?**

```python
def generate_thumbnails(file_id: str, s3_key: str, content_type: str):
    if not content_type.startswith("image/"):
        return  # only for images
    
    # Download original from S3
    original = s3.get_object(Bucket="uploads", Key=s3_key)['Body'].read()
    
    # Generate multiple sizes using Pillow
    from PIL import Image
    import io
    
    img = Image.open(io.BytesIO(original))
    
    thumbnail_urls = {}
    for size, (width, height) in [("small", (100, 100)), ("medium", (300, 300)), 
                                    ("large", (800, 800))]:
        thumb = img.copy()
        thumb.thumbnail((width, height), Image.LANCZOS)
        
        buffer = io.BytesIO()
        thumb.save(buffer, format="JPEG", quality=85)
        buffer.seek(0)
        
        thumb_key = f"thumbnails/{file_id}_{size}.jpg"
        s3.put_object(Bucket="uploads", Key=thumb_key, 
                     Body=buffer, ContentType="image/jpeg",
                     ACL="public-read")  # thumbnails are public
        
        thumbnail_urls[size] = f"https://cdn.example.com/{thumb_key}"
    
    # Update file record with thumbnail URLs
    db.update_file(file_id, {
        "thumbnail_small": thumbnail_urls["small"],
        "thumbnail_medium": thumbnail_urls["medium"],
        "thumbnail_large": thumbnail_urls["large"],
        "status": "complete"
    })
```

Total thumbnail generation time: 3-10 seconds per image. File shows as 'processing' during this. Client receives webhook or polls for status change to 'complete'.
