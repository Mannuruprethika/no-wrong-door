# AI Usage

## Overview

AI assistance was used as a development support tool during the implementation of the No Wrong Door project.

The final implementation was reviewed and tested locally in the Windows and VS Code development environment.

AI assistance was primarily used for:

- Understanding the project requirements.
- Planning the adapter/service architecture.
- Explaining Python implementation details.
- Troubleshooting runtime and connection errors.
- Improving error handling and graceful degradation.
- Designing and reviewing identity matching logic.
- Suggesting test cases and validation scenarios.
- Preparing project documentation.

## Human Review and Validation

AI-generated suggestions were not treated as automatically correct.

The implementation was manually reviewed and executed locally.

The following behavior was tested:

- Resident Index pagination.
- Duplicate resident protection.
- Benefits Register retrieval.
- Benefits Register retry behavior.
- Unified service operation.
- Resident lookup.
- High-confidence identity matching.
- Unmatched residents.
- Unknown resident IDs.
- Resident Index unavailable scenario.
- Benefits Register unavailable scenario.
- Repeated read requests.
- Unified API health endpoint.

## Verified Test Data

The local test environment returned:

```text
Resident Index records : 620
Benefits records       : 540
High-confidence matches: 306
Unmatched residents    : 314
```

A verified high-confidence example was:

```text
Resident ID    : R-10451
Resident       : Tomas Grady
Benefits Ref   : NO/2015/4451
Score          : 100
Confidence     : high
Matched fields: name, date_of_birth, address, town
```

## Error Handling Validation

The project was also tested when one of the source services was unavailable.

When the Benefits Register was unavailable, the Unified API continued to
return resident information and reported the Benefits source as unavailable.

When the Resident Index was unavailable, the Benefits Register could still
be queried, but identity matching was not attempted because the resident
identity could not be established.

## Role of AI

AI was used as a development assistant rather than as a replacement for
testing or engineering judgment.

The final behavior of the application was determined by the actual local
implementation and the observed test results.

## Data Handling

The project uses locally provided/mock source-system data for development and
testing.

No external production system was intentionally accessed as part of the
implementation described in this repository.
