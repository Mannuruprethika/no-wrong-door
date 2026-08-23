# Architecture Decisions

## 1. Source Adapter Separation

The project keeps the Resident Index and Benefits Register behind separate
adapter classes.

- `ResidentAdapter` communicates with the Resident Index REST service.
- `BenefitsAdapter` communicates with the Benefits Register service.
- `UnifiedResidentService` combines the results.
- `IdentityMatcher` is responsible for matching a resident with benefits data.

This keeps source-specific communication separate from the unified business
logic.

## 2. Pagination Strategy

The Resident Index is retrieved page by page.

The adapter continues requesting pages while:

```text
has_more = true
```

Each page is processed independently.

A stable Resident Index ID is used to prevent duplicate residents from being
returned when the same record appears on multiple pages.

Example:

```python
seen_ids = set()
```

A resident is added only when its ID has not already been seen.

Malformed records without an ID are ignored.

## 3. Benefits Retrieval

The Benefits Register is retrieved through its dedicated adapter.

The unified service does not directly communicate with the Benefits Register.

This keeps source-specific behavior inside the adapter and allows the
Benefits integration to handle its own communication and retry behavior.

## 4. Graceful Degradation

The unified service treats the Resident Index and Benefits Register as
independent sources.

A failure in one source does not cause the complete unified API request to
fail.

### Benefits Register unavailable

If the Resident Index is available but the Benefits Register is unavailable:

```text
Resident Index    -> success
Benefits Register -> unavailable
Unified API       -> response returned
```

Resident information is still returned.

The Benefits status is reported as:

```text
status: unavailable
```

The source failure reason is also exposed.

### Resident Index unavailable

If the Resident Index is unavailable but the Benefits Register is available:

```text
Resident Index    -> unavailable
Benefits Register -> success
Unified API       -> response returned
```

The Benefits Register is still queried.

No resident identity match is attempted because the resident identity cannot be
established.

This prevents one unavailable source from taking down the complete service.

## 5. Retry Behavior

Source adapters use retry behavior where required by the source integration.

The Benefits Register integration retries a failed request before reporting
the source as unavailable.

The observed retry behavior is:

```text
Benefits Register attempt 1/3 failed
Benefits Register attempt 2/3 failed
Benefits Register attempt 3/3 failed
```

If all attempts fail, the failure is returned as an explicit source
availability error rather than causing the complete unified service to fail.

## 6. Identity Matching

The project includes an identity matching component that compares Resident
Index records with Benefits Register records.

The matcher considers multiple identity attributes:

- Name
- Date of birth
- Address
- Town

The result includes:

- Match status
- Confidence
- Score
- Matched fields
- Benefits record when a match is found

A high-confidence match is produced when the required identity information
matches strongly.

A verified example:

```text
Resident       : Tomas Grady
Resident ID    : R-10451
Benefits Ref   : NO/2015/4451
Score          : 100
Confidence     : high
Fields         : name, date_of_birth, address, town
```

## 7. No False Match When Resident Is Missing

If the requested Resident ID does not exist in the Resident Index, the service
does not attempt identity matching.

The response reports:

```text
resident_index -> not_found
benefits       -> not_matched
```

This avoids creating a benefits association without a known resident identity.

The behavior was tested with:

```text
R-99999
```

and the Resident Index correctly reported the resident as not found.

## 8. Failure Transparency

Source failures are not silently converted into empty datasets.

When a source is unavailable, the response includes:

```text
status: unavailable
reason: <source failure reason>
```

This allows callers to distinguish between:

- No matching record
- Source unavailable
- Successful source retrieval

This distinction is important because an unavailable source must not be
interpreted as an empty source.

## 9. Idempotent Read Operations

The unified API performs read-only operations.

Repeated requests for the same Resident ID do not create or modify records.

For example:

```text
GET /resident/R-10451
```

was executed repeatedly and returned the same logical result:

```text
Resident       : Tomas Grady
Benefits       : matched
Confidence     : high
Score          : 100
Benefits Ref   : NO/2015/4451
```

## 10. Unified Service Responsibility

`UnifiedResidentService` is responsible for orchestration rather than
source-specific communication.

Its responsibilities are:

- Retrieve Resident Index data.
- Retrieve Benefits Register data.
- Handle source failures.
- Preserve partial availability.
- Locate a requested resident.
- Invoke identity matching when appropriate.
- Assemble the unified response.

The individual adapters remain responsible for communicating with their
respective source systems.

## 11. Design Goal

The design prioritizes:

- Independent source integrations
- Clear failure reporting
- Partial availability
- Duplicate protection
- Safe repeated reads
- Deterministic identity matching
- Simple local development and testing

The implementation intentionally avoids unnecessary infrastructure such as a
database, authentication layer, or UI because these are not required for the
core challenge.
