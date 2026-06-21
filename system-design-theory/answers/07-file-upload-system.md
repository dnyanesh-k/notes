# Q7: Design File Upload System (S3-like)

---

## Clarifying Questions

First — what kinds of files are we handling? Small documents, or large files like video (multi-GB)? Large files require chunked uploads — you can't send 4GB in a single HTTP request reliably.

Who are the users — internal teams or external consumers? Is this a public object storage API (like AWS S3) or a product feature like "upload your profile picture"?

What are the durability and availability requirements? S3 promises 11 nines of durability — that means replication across multiple data centers. Are we targeting that, or is single-region sufficient?

Do we need access control — private files, public files, temporary signed URLs? And do we need versioning — keeping old versions of an uploaded file?

*Assuming: general-purpose file storage for external developers (S3-like), files from 1KB to 5GB, chunked uploads for large files, high durability (replicated across 3 zones), signed URLs for access control, no versioning for now.*

---

## Scope

I'll design: file upload (both small single-request and large chunked multipart), file download, metadata management, and access control via signed URLs. I'll skip versioning, lifecycle policies, and cross-region replication.

Scale: 50M DAU, 10M file uploads/day = 115 uploads/sec. Average file size 10MB = 1.15 GB/sec upload throughput. Downloads are 10x more — 1.15 TB/sec download throughput (CDN handles most of this).

---

## High Level Design

```
┌──────────┐                                                            ┌───────────┐
│  Client  │──Small file (< 100MB)──▶┌────────────────┐              │           │
│          │                          │  Upload Service │─────────────▶│    S3     │
│          │──Large file multipart──▶ └────────┬───────┘   chunks     │  (Object  │
│          │◀──pre-signed URL────────           │                       │  Storage) │
└──────────┘                                    │                       │           │
      │                                         ▼                       └─────┬─────┘
      │                                  ┌─────────────┐                     │
      │◀─── download ─────────────────── │   CDN       │◀────────────────────┘
      │                                  └─────────────┘
      │
      ▼
┌──────────────────────────────────────────────┐
│              Metadata Service                 │
│  MySQL: file_id, user_id, bucket, key,        │
│         size, checksum, storage_path, status  │
└──────────────────────────────────────────────┘

Flow for direct upload (small files):
  Client → Upload Service → S3 → return file_id

Flow for pre-signed URL (large files / direct-to-S3):
  Client → Metadata Service (register upload intent)
         ← pre-signed S3 URL (valid 1 hour)
  Client → uploads directly to S3 (bypasses our servers)
  S3 → triggers event → Upload Service marks upload complete
```

The pre-signed URL pattern is critical for large files — it offloads the actual bytes from our servers directly to S3. Our servers never see the file content for large uploads.

---

## Low Level Design

### Small File Upload (< 100MB)

```
POST /v1/files
  Headers: Content-Type: image/jpeg, Content-Length: 5242880
  Body: (binary file data)
  Response 201: { "file_id": "f_abc123", "url": "https://cdn.example.com/f_abc123" }
```

```
Upload Service flow:
1. Validate: content-type, file size, user quota check
2. Generate file_id (UUID or Snowflake)
3. Compute checksum (MD5/SHA256) of incoming bytes
4. Stream bytes to S3: PUT s3://bucket/{user_id}/{file_id}
5. Save metadata to MySQL
6. Return file_id + CDN URL
```

---

### Large File Upload — Chunked Multipart

For files > 100MB, single HTTP upload is unreliable — network drops mean re-uploading everything. Chunked upload allows resuming from where you left off.

```
Step 1: Initiate upload
  POST /v1/uploads/multipart/init
  Body: { "filename": "video.mp4", "size": 4294967296, "content_type": "video/mp4" }
  Response 200: {
    "upload_id": "mp_xyz789",
    "chunk_size": 10485760,    -- 10MB chunks
    "total_chunks": 410
  }

Step 2: Upload each chunk (can be parallelized — 4 chunks at a time)
  PUT /v1/uploads/multipart/{upload_id}/chunks/{chunk_number}
  Body: (10MB binary chunk)
  Response 200: { "chunk_number": 1, "checksum": "abc..." }

Step 3: Complete the upload (after all chunks uploaded)
  POST /v1/uploads/multipart/{upload_id}/complete
  Body: { "checksums": ["abc...", "def...", ...] }  -- per-chunk checksums
  Response 200: { "file_id": "f_abc123", "url": "..." }

Step 4: Resume after network drop
  GET /v1/uploads/multipart/{upload_id}/status
  Response 200: { "uploaded_chunks": [1,2,3,5], "missing_chunks": [4,6,...] }
  -- Client retries only missing chunks
```

Server-side: S3 has native multipart upload support. Each chunk is uploaded as an S3 part. On completion, S3 assembles all parts into the final object atomically.

---

### Data Model

```sql
CREATE TABLE files (
    file_id       VARCHAR(36) PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    bucket        VARCHAR(100) NOT NULL,
    storage_key   VARCHAR(500) NOT NULL,      -- S3 key
    filename      VARCHAR(500) NOT NULL,
    content_type  VARCHAR(100) NOT NULL,
    size_bytes    BIGINT NOT NULL,
    checksum      VARCHAR(64) NOT NULL,        -- SHA256 of full file
    status        ENUM('uploading','complete','deleted') DEFAULT 'uploading',
    is_public     BOOLEAN DEFAULT FALSE,
    created_at    DATETIME NOT NULL DEFAULT NOW(),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status, created_at)
);

CREATE TABLE multipart_uploads (
    upload_id     VARCHAR(36) PRIMARY KEY,
    user_id       BIGINT NOT NULL,
    s3_upload_id  VARCHAR(200),               -- S3's multipart upload ID
    filename      VARCHAR(500),
    total_chunks  INT NOT NULL,
    chunk_size    INT NOT NULL,
    status        ENUM('in_progress','complete','aborted') DEFAULT 'in_progress',
    created_at    DATETIME NOT NULL,
    expires_at    DATETIME NOT NULL           -- auto-abort stale uploads after 24h
);

CREATE TABLE upload_chunks (
    upload_id     VARCHAR(36) NOT NULL,
    chunk_number  INT NOT NULL,
    checksum      VARCHAR(64),
    uploaded_at   DATETIME,
    PRIMARY KEY (upload_id, chunk_number)
);
```

---

### Pre-signed URLs for Direct Client-to-S3 Upload

For large files, routing bytes through our servers wastes bandwidth and adds latency. Pre-signed URLs let the client upload directly to S3 with temporary credentials.

```
Client: POST /v1/uploads/presigned-url
  Body: { "filename": "video.mp4", "content_type": "video/mp4", "size": 4294967296 }

Server:
  1. Validate user quota
  2. Generate S3 pre-signed PUT URL (AWS SDK):
     url = s3.generate_presigned_url(
       'put_object',
       Params={'Bucket': 'uploads', 'Key': f'{user_id}/{file_id}'},
       ExpiresIn=3600  # 1 hour validity
     )
  3. Register pending upload in MySQL (status='uploading')
  4. Return pre-signed URL

Client: PUT {presigned_url} (directly to S3, no server in the middle)

S3 triggers S3 Event Notification → Lambda/SQS:
  - Upload Service marks file status='complete'
  - Initiates virus scan, thumbnail generation if needed
```

This is the standard pattern for any file upload in production. Our servers handle metadata; S3 handles bytes.

---

### Access Control — Signed Download URLs

For private files, don't expose the S3 URL directly. Instead:

```
GET /v1/files/{file_id}/download
  Headers: Authorization: Bearer <user_token>

Server:
  1. Check file ownership: does this user own file_id?
  2. Generate pre-signed GET URL, valid 15 minutes:
     url = s3.generate_presigned_url('get_object', ..., ExpiresIn=900)
  3. Return { "download_url": "https://s3.amazonaws.com/...?Signature=..." }

Client redirects to the pre-signed URL.
```

For public files: store in a separate S3 bucket with public-read ACL. Serve via CloudFront CDN. URL is permanent: `https://cdn.example.com/{file_id}`.

---

### Virus Scanning Pipeline

Every uploaded file should be scanned before being accessible.

```
Upload complete
      │
      ▼
SQS Queue (scan.pending)
      │
      ▼
Antivirus Worker (ClamAV or cloud AV API)
      │
 ┌────┴────┐
 ▼         ▼
Clean    Infected
  │           │
  ▼           ▼
Mark file   Delete file
status=     from S3
'available' Notify user
```

Files are in status='uploading' until scan completes. The client polls or listens via WebSocket for the status update. This adds 5–30 seconds before the file is accessible — expected and acceptable.

---

## Scale — What Breaks at 10x?

At 1,150 uploads/sec, 11.5 GB/sec upload throughput:

**S3 bandwidth:** S3 scales essentially infinitely — it's AWS's backbone storage. The bottleneck is our Upload Service bandwidth for small files. Run Upload Service on high-network instances (25Gbps+) and scale horizontally. For large files via pre-signed URLs, our servers are completely out of the bandwidth path.

**Metadata DB (MySQL):** At 1,150 file records/sec, MySQL handles this easily — it can sustain 10K+ writes/sec. The download queries (`WHERE file_id = ?`) are indexed — sub-millisecond. Add read replicas for download URL generation.

**CDN:** Downloads are 10x uploads = 115 GB/sec. CloudFront or Cloudflare cache popular files at edge. S3 only handles cache misses. For truly popular content (profile pictures, logo images), CDN hit rate is >99%.

**Virus scan throughput:** At 1,150 files/sec, scanning is the bottleneck. Scale AV workers horizontally — each worker processes one file at a time. 1,150 workers might be too many — AV scanning takes 0.1–1 second per file, so 100 workers handle 100–1000 scans/sec. Use an auto-scaling group based on SQS queue depth.

---

## Trade-offs

**Single large object vs chunking:** S3 supports objects up to 5TB as a single upload. Chunked multipart upload is required for objects > 100MB by S3's recommendation. The benefit of chunking isn't just reliability — parallel chunk uploads (4 chunks simultaneously) can saturate the client's upload bandwidth fully, reducing total upload time 4x.

**Client-side vs server-side checksum:** Computing checksum client-side before uploading lets us detect corruption or duplicates before storage costs are incurred. Server recomputes checksum after receiving and compares — if they disagree, the upload is corrupt. This detects bit-flip errors in transit that TCP doesn't catch (TCP checksums are weak). SHA256 is correct here — MD5 has collision vulnerabilities.

**Deduplication:** If two users upload identical files (same checksum), we could store only one copy and reference it from both accounts. This is called content-addressable storage. It saves storage but creates security concerns — User A could potentially infer that User B has the same file if they see a fast "already exists" response. The privacy risk usually outweighs the storage savings except in specific use cases.

---

## Cross-Questions

**How do you handle an upload that gets interrupted at chunk 200 of 410?**

The client fetches upload status: `GET /v1/uploads/multipart/{upload_id}/status`. Server returns which chunks are present (stored in MySQL `upload_chunks`). Client resumes from chunk 201. S3 multipart upload holds all previously uploaded parts for 24 hours (configurable). No re-uploading of already-completed chunks. This is exactly how AWS S3 Transfer Acceleration and most mobile SDKs work.

**How do you prevent a user from exceeding their storage quota?**

Each user has a quota stored in MySQL (`user_quota` table: `used_bytes`, `limit_bytes`). Before accepting an upload, the Upload Service checks: `used_bytes + incoming_size <= limit_bytes`. If over quota, return 429 with a message. Use an optimistic approach — update `used_bytes` atomically with the upload completion (SQL transaction). If the upload fails, decrement back. Don't decrement on delete synchronously — use a background job to reconcile used_bytes with actual S3 storage daily.

**How do you handle a corrupted chunk?**

Each chunk has a checksum (MD5 or SHA256). The client computes it before sending. The server recomputes after receiving. If they disagree, return 400 for that chunk with an error. The client retries that specific chunk. On final assembly, S3 also validates the ETag of each part. Multi-layer checksum validation catches corruption at network, memory, and storage layers.

**How would you implement file sharing between users?**

Add an `acl` table: `{ file_id, grantee_user_id, permission: read|write, expires_at }`. When generating a download URL, check both ownership and ACL. For link-based sharing (like Google Drive's "anyone with link"), generate a random `share_token` for the file. The download endpoint accepts `?token={share_token}` without requiring auth — server validates the token against the database. The token can have an expiry. Don't put the share token in the pre-signed S3 URL — keep it in your application layer so you can revoke access by deleting the token from DB, even if the S3 URL hasn't expired.

**How would you generate image thumbnails automatically after upload?**

Add a thumbnail job to the post-upload pipeline. After virus scan passes, publish to `thumbnail.generate` Kafka topic. A Thumbnail Worker uses ImageMagick or Pillow to resize the original to standard sizes (100x100, 300x300, 800x800). Upload each thumbnail to S3 with a naming convention: `{file_id}_thumb_100.jpg`. Store thumbnail URLs in the files metadata table. The CDN serves thumbnails like any other file. Total time from upload completion to thumbnails available: 5–15 seconds. The client shows a loading state until the webhook fires indicating thumbnails are ready.
