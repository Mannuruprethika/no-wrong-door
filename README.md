# No Wrong Door — Unified Resident API

A Python service that combines data from two independent source systems:

- Resident Index
- Benefits Register

The project provides a unified API for looking up a resident and determining whether a corresponding Benefits Register record can be matched.

## Architecture

```text
                    ┌─────────────────────┐
                    │     Unified API      │
                    │       app.py         │
                    │        :8000         │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ UnifiedResident     │
                    │ Service             │
                    └─────────┬───────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
       ┌──────────────────┐      ┌──────────────────┐
       │ Resident Adapter │      │ Benefits Adapter │
       └────────┬─────────┘      └────────┬─────────┘
                │                         │
                ▼                         ▼
       Resident Index              Benefits Register
          :8081                         :8082

                    ┌─────────────────────┐
                    │   Identity Matcher  │
                    └─────────────────────┘
```

## Project Structure

```text
no-wrong-door/
│
├── adapters/
│   ├── resident_adapter.py
│   └── benefits_adapter.py
│
├── services/
│   ├── unified_service.py
│   └── identity_matcher.py
│
├── tests/
├── app.py
├── README.md
├── DECISIONS.md
└── AI-USAGE.md
```

## Requirements

- Python 3.x
- VS Code
- PowerShell
- Windows

## Running the Project

The project uses three local services:

| Service | Port | Purpose |
|---|---:|---|
| Resident Index | 8081 | Resident data |
| Benefits Register | 8082 | Benefits data |
| Unified API | 8000 | Unified resident lookup |

Run each service in a separate PowerShell terminal.

### 1. Start Resident Index

```powershell
python services/rest_service.py
```

Resident Index:

```text
http://127.0.0.1:8081
```

### 2. Start Benefits Register

```powershell
python services/xml_service.py
```

Benefits Register:

```text
http://127.0.0.1:8082
```

### 3. Start Unified API

```powershell
python app.py
```

Unified API:

```text
http://127.0.0.1:8000
```

## Health Check

```powershell
curl.exe http://127.0.0.1:8000/health
```

Expected:

```json
{
  "status": "ok",
  "service": "No Wrong Door Unified API"
}
```

## API

### Resident Lookup

```text
GET /resident/{resident_id}
```

Example:

```powershell
curl.exe http://127.0.0.1:8000/resident/R-10451
```

Verified successful result:

```text
Resident       : Tomas Grady
Resident ID    : R-10451
Benefits Ref   : NO/2015/4451
Confidence     : high
Score          : 100
Benefit Code   : HSP-A
Review Due     : 2026-04-29
```

### No Match

```powershell
curl.exe http://127.0.0.1:8000/resident/R-10394
```

Expected behavior:

```text
benefits.status       -> not_matched
benefits.confidence   -> none
benefits.score        -> 0
benefits.data         -> null
```

### Unknown Resident

```powershell
curl.exe http://127.0.0.1:8000/resident/R-99999
```

Expected behavior:

```text
Resident Index -> not_found
Benefits       -> not_matched
```

No identity match is attempted when the resident does not exist.

## Identity Matching

The matcher compares:

- Name
- Date of birth
- Address
- Town

The result contains match status, confidence, score, matched fields, and the benefits record when a match is found.

Verified results:

```text
Residents checked : 620
Benefits checked  : 540
High confidence   : 306
Unmatched         : 314
```

Example high-confidence match:

```text
Resident : Tomas Grady
Resident ID : R-10451
Benefits Ref : NO/2015/4451
Score : 100
Fields : name, date_of_birth, address, town
```

## Pagination and Duplicate Protection

The Resident Index is retrieved page by page while `has_more` is true.

The adapter:

1. Requests each page.
2. Processes the page independently.
3. Ignores malformed records without an ID.
4. Uses a `seen_ids` set to prevent duplicates.
5. Continues until the source reports that no more pages exist.

Verified Resident Index result:

```text
Unique residents: 620
```

## Graceful Degradation

The Resident Index and Benefits Register are independent sources.

### Benefits Register unavailable

```text
Resident Index    -> success
Benefits Register -> unavailable
Unified API       -> response returned
```

Resident information remains available and the source failure reason is exposed.

### Resident Index unavailable

```text
Resident Index    -> unavailable
Benefits Register -> success
Unified API       -> response returned
```

The Benefits source can still be queried, but identity matching is not attempted because the resident identity cannot be established.

## Retry Behavior

The Benefits Register integration retries failed requests before reporting the source as unavailable.

Observed during testing:

```text
Benefits Register attempt 1/3 failed
Benefits Register attempt 2/3 failed
Benefits Register attempt 3/3 failed
```

After all attempts fail, the source is explicitly reported as unavailable instead of being silently treated as an empty dataset.

## Failure Transparency

Source failures include:

```text
status: unavailable
reason: <source failure reason>
```

This distinguishes between:

- Successful source retrieval
- No matching record
- Source unavailable

## Idempotent Read Operations

The API performs read-only operations. Repeating the same resident lookup does not create or modify records.

The following request was tested repeatedly:

```powershell
curl.exe http://127.0.0.1:8000/resident/R-10451
```

The same logical result was returned each time:

```text
Resident       : Tomas Grady
Benefits       : matched
Confidence     : high
Score          : 100
Reference      : NO/2015/4451
```

## Testing

Run the available tests from the project root:

```powershell
python test_resident_adapter.py
python test_benefits_adapter.py
python test_benefits_sample.py
python test_unified_service.py
python test_identity_matching.py
python test_identity_samples.py
```

## Tested Scenarios

1. Both source systems available.
2. Benefits Register unavailable.
3. Resident Index unavailable.
4. Unknown Resident ID.
5. Resident with no benefits match.
6. High-confidence identity match.
7. Repeated read of the same resident.
8. Paginated Resident Index retrieval.
9. Duplicate resident protection.

## API Summary

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check Unified API health |
| GET | `/resident/{resident_id}` | Retrieve unified resident information |

## Architecture Decisions

### Source Adapter Separation

`ResidentAdapter` communicates with the Resident Index. `BenefitsAdapter` communicates with the Benefits Register. `UnifiedResidentService` orchestrates both sources, while `IdentityMatcher` handles identity matching.

This keeps source-specific communication separate from business logic.

### Pagination Strategy

Resident data is retrieved page by page. The adapter continues while `has_more` is true and uses the stable resident ID to prevent duplicate records.

### Benefits Retrieval

Benefits data is retrieved only through the dedicated Benefits Adapter. The unified service does not directly communicate with the source system.

### Graceful Degradation

A failure in one source does not take down the complete unified API. Partial results and explicit source availability information are preserved.

### Retry Behavior

Failed Benefits Register requests may be retried before the source is reported as unavailable.

### Identity Matching

Identity matching uses name, date of birth, address, and town and returns a score, confidence level, matched fields, and benefits data when appropriate.

### No False Match

If a requested resident does not exist in the Resident Index, identity matching is not attempted.

### Unified Service Responsibility

`UnifiedResidentService` is responsible for orchestration:

- Retrieve source data.
- Handle source failures.
- Preserve partial availability.
- Locate residents.
- Invoke identity matching when appropriate.
- Assemble the unified response.

Adapters remain responsible for source-specific communication.

## Design Goals

The design prioritizes:

- Independent source integrations
- Clear failure reporting
- Partial availability
- Duplicate protection
- Safe repeated reads
- Deterministic identity matching
- Simple local development and testing

The implementation intentionally avoids unnecessary infrastructure such as a database, authentication layer, or UI because these are not required for the core challenge.

## Development Environment

Developed and tested locally using:

- Windows
- PowerShell
- VS Code
- Python 3.x

The project uses the provided Resident Index and Benefits Register services as its source systems.
