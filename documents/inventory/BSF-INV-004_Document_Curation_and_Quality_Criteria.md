# BSF-INV-004 — Document Curation and Quality Criteria

**BlueSea Foods | Document Control and RAG Readiness**

## Document Control

| Field | Value |
| --- | --- |
| Document Code | BSF-INV-004 |
| Document Title | Document Curation and Quality Criteria |
| Version | 1.0 |
| Document Owner | Knowledge Management Lead |
| Effective Date | 2026-07-21 |
| Source Review Format | Markdown |
| Target Export Format | Markdown / DOCX derivative when required |
| Confidentiality | Internal / Controlled |
| Review Cycle | Quarterly during RAG build; annual after stabilization |
| Status | Ready for review |
| Keywords | document curation; quality criteria; completeness; metadata; RAG readiness; source acceptance; governance |

## Purpose

This document defines the minimum quality criteria used to accept, correct, reject, or defer BlueSea Foods documents before they are indexed in the corporate RAG environment. It protects retrieval quality, source traceability, access control, and audit readiness.

## 1. Scope

This procedure applies to all BlueSea Foods documents, spreadsheets, structured data files, training materials, HTML manuals, and controlled references proposed for inclusion in the corporate knowledge base or RAG index.

It is used by Document Control, document owners, Knowledge Management, Information Security, Quality, and technical RAG teams before ingestion, after revision, and during periodic quality reviews.

The criteria do not replace formal approval workflows. They establish whether a source is usable for retrieval and whether the source can safely support answers, citations, and operational guidance.

## 2. Curation Principles

- **Authoritative source first:** approved controlled documents take priority over drafts, copies, screenshots, and informal notes.
- **Traceability by design:** each accepted source must keep a stable document code, version, owner, confidentiality label, and source path.
- **Readable before searchable:** documents must be understandable to a human reviewer before they are indexed for machine retrieval.
- **Permission-aware content:** confidential content must not be indexed into an audience that is broader than the approved access group.
- **Correction over deletion:** minor issues should be corrected where possible, while obsolete, duplicate, or uncontrolled records are rejected or archived.
- **No orphan sources:** every ingested source must have a responsible owner and review cycle.

**Quality standard:** A source is RAG-ready only when it is accurate enough to guide a user, structured enough to retrieve reliably, controlled enough to cite, and permissioned enough to prevent unauthorized exposure.

## 3. Quality Dimensions

| Dimension | Criterion | Evidence |
| --- | --- | --- |
| Authority | Source is approved, owned, and aligned with the document inventory. | Owner, approver, version, effective date. |
| Completeness | Required sections, tables, attachments, references, and records are present. | No placeholder text, missing sections, or unresolved notes. |
| Accuracy | Facts, process steps, roles, limits, and references are internally consistent. | No contradictions with newer approved documents. |
| Structure | Headings, tables, lists, worksheets, or records support clean chunking and citation. | Logical sections and machine-readable source anchors. |
| Metadata | Code, title, area, owner, confidentiality, keywords, review date, and related documents are available. | Minimum metadata fields completed. |
| Access Control | Confidentiality and role access match the intended retrieval audience. | Permission label and approved access group. |
| Retrieval Utility | The source can answer expected user questions with clear citations. | Test questions pass with correct source retrieval. |

## 4. Acceptance Scoring

Each proposed source is scored before production ingestion. The score supports review decisions, but mandatory failures still block release even when the total score is high.

| Dimension | Weight | Pass Condition | Fail Condition |
| --- | ---: | --- | --- |
| Authority | 20 | Approved source, owner and version confirmed. | Unapproved, obsolete, or owner unknown. |
| Completeness | 15 | No missing sections, unresolved comments, or placeholders. | Missing required content or incomplete tables. |
| Accuracy and consistency | 20 | Matches controlled references and operational practice. | Contradicts a newer source or includes unverified claims. |
| Structure and readability | 15 | Clear headings, stable tables, readable text, extractable content. | Scanned image-only text, broken tables, or poor OCR. |
| Metadata quality | 15 | Required metadata fields complete and aligned with inventory. | Missing code, owner, confidentiality, keywords, or review date. |
| Access and confidentiality | 15 | Permission label and access group approved. | Confidential source lacks access mapping. |

| Score | Decision | Required Action |
| --- | --- | --- |
| 90-100 | Accept for production ingestion | Release after retrieval test pass. |
| 75-89 | Accept with minor corrections | Correct metadata, formatting, or small clarity issues before release. |
| 60-74 | Defer | Return to owner with corrective actions and re-score. |
| Below 60 | Reject for current wave | Do not index until source is substantially corrected or replaced. |

## 5. Mandatory Rejection Criteria

| Criterion | Risk | Decision |
| --- | --- | --- |
| No approved owner | Source cannot be governed, corrected, or reviewed. | Reject until owner is assigned. |
| Obsolete version | Retrieval may return superseded instructions. | Replace with current approved version. |
| Unresolved confidentiality | Risk of unauthorized disclosure. | Hold until Information Security approves access label. |
| Unusable content extraction | RAG cannot cite or retrieve content reliably. | Improve source file, OCR, or structured export. |
| Contradicts current controlled procedure | Creates operational or audit risk. | Escalate to Document Control and relevant owner. |
| Placeholder or draft-only content | Not reliable as an authoritative source. | Use only in restricted test index, if needed. |

## 6. Curation Workflow

| Step | Activity | Minimum Control | Output |
| ---: | --- | --- | --- |
| 1 | Receive source package | Confirm file, document code, proposed format, owner, and target ingestion wave. | Curation intake record |
| 2 | Check control metadata | Verify document control table, version, confidentiality, review cycle, keywords, and related documents. | Metadata checklist |
| 3 | Review content quality | Assess completeness, clarity, consistency, references, and operational usefulness. | Quality score |
| 4 | Check extraction readiness | Confirm text, tables, worksheets, slides, or records can be extracted without loss. | Extraction pass/fail |
| 5 | Confirm access mapping | Validate permitted audiences and deny broader access when classification is unclear. | Access label |
| 6 | Run retrieval test | Ask representative questions and verify correct answer, source, citation, and role behavior. | QA test log |
| 7 | Approve, correct, defer, or reject | Record decision and required actions in the inventory or issue tracker. | Final disposition |

## 7. Format-Specific Quality Criteria

| Format | Pass Criteria | Common Blockers |
| --- | --- | --- |
| DOCX | Headings are real styles where possible; tables are readable; control table is complete; logo/header does not interfere with content. | Broken page layout, missing control metadata, unreadable tables. |
| Markdown | Headings, lists, and tables are valid; document code and metadata are clear; no hidden dependencies on external styling. | Ambiguous structure or missing document control block. |
| XLSX | Worksheet names are meaningful; headers are present; formulas calculate; key columns have validation; no hidden critical data. | Formula errors, blank key fields, unclear sheet purpose. |
| CSV | UTF-8 encoding, stable headers, unique identifiers where required, no mixed delimiter, no blank critical fields. | Duplicate document codes, broken rows, or inconsistent columns. |
| JSON | Valid syntax, consistent schema, meaningful keys, controlled values, and no trailing comments. | Invalid JSON or inconsistent object structure. |
| PPTX | Each slide has a clear title; visible text is extractable; notes are approved if ingested; diagrams have explanatory text. | Image-only slides without descriptive text. |
| HTML | Semantic sections, stable anchors, accessible tables, embedded or stable assets, and no broken internal links. | Broken anchors, missing sections, or script-dependent core content. |

## 8. Metadata Quality Checklist

| Field | Quality Expectation | Status |
| --- | --- | --- |
| Document code | Matches official inventory and filename. | Required |
| Title | Matches cover, header, inventory, and source path. | Required |
| Business area | Uses approved area list. | Required |
| Owner and backup | Named role or position responsible for content. | Required |
| Approver | Business or functional approver identified. | Required for controlled sources |
| Confidentiality | Internal Use or Confidential - Internal. | Required |
| Access group | Mapped to approved user roles. | Required before release |
| Keywords | Includes process, system, standard, synonym, and retrieval terms. | Required |
| Review date | Future date or documented exception. | Required |
| Related documents | Cross-references key dependencies. | Recommended |

## 9. Retrieval Quality Tests

| Test Type | Scenario | Pass Behavior |
| --- | --- | --- |
| Exact lookup | User asks for a specific document, code, role, limit, or requirement. | Correct document and citation returned. |
| Procedure question | User asks how to perform a process step. | Answer follows the approved workflow and cites source section. |
| Cross-document question | User asks a topic covered by multiple documents. | Answer cites the best authority and distinguishes supporting sources. |
| Conflict check | Two sources appear to say different things. | Newest or more authoritative source is preferred; conflict is flagged. |
| Permission test | User lacks access to confidential content. | System refuses or summarizes only allowed information. |
| Staleness test | Source review date is expired or near expiry. | Response includes stale-source warning and owner routing. |

**Citation rule:** A RAG answer is not considered quality-approved unless it can point back to the correct source document, version, and relevant section or structured record.

## 10. Correction and Escalation Rules

| Correction Type | Examples | Required Owner |
| --- | --- | --- |
| Minor correction | Typos, inconsistent capitalization, incomplete keywords, or small formatting issues. | Document Controller may correct and log change. |
| Owner correction | Missing section, unclear role, process ambiguity, or incomplete evidence. | Return to document owner before ingestion. |
| Security escalation | Ambiguous confidentiality, personal data, restricted commercial terms, or system access details. | Information Security approval required. |
| Quality escalation | Content conflicts with QMS, certification, HACCP, BRCGS, IFS, MSC, BASC, SMETA, or audit commitments. | Quality Management review required. |
| Technical remediation | OCR failure, broken spreadsheet formulas, inaccessible HTML, or invalid JSON. | RAG Technical Lead corrects extraction path or requests source replacement. |

## 11. Quality Metrics

| Metric | Definition | Frequency |
| --- | --- | --- |
| Source acceptance rate | Accepted sources divided by reviewed sources. | By wave |
| Metadata completeness | Required metadata fields completed per document. | Weekly during build |
| Retrieval precision sample | Correct answer and citation in representative test questions. | Each release |
| Permission test pass rate | Restricted content blocked or limited correctly. | Each release |
| Stale-source count | Indexed sources past review date. | Monthly |
| Correction cycle time | Average business days from issue to corrected source. | Monthly |
| Duplicate-source count | Sources with overlapping title/code/content requiring consolidation. | Monthly |

## 12. Records

| Record | Purpose | Responsible Role |
| --- | --- | --- |
| Curation intake log | Document received, source path, owner, target wave, reviewer. | Document Control |
| Quality scoring sheet | Score by dimension, mandatory blockers, disposition. | Knowledge Management |
| Metadata checklist | Required and recommended metadata fields. | Document Control |
| Retrieval QA log | Questions, expected source, actual source, citation, result. | RAG Technical Lead |
| Exception register | Approved deviations, owner, expiry date, compensating control. | Knowledge Management |
| Correction tracker | Issues, owner, due date, status, closure evidence. | Document Controller |

## 13. Internal References

| Code | Document |
| --- | --- |
| BSF-INV-001 | Document Inventory |
| BSF-INV-002 | Document Ownership Matrix |
| BSF-INV-003 | Document Sources and Ingestion Plan |
| BSF-INV-005 | Access and Permissions Policy |
| BSF-DOC-STD-001 | Corporate Document Standard |
| BSF-CORP-004 | Corporate Knowledge Map |
| BSF-QMS-002 | Certification and Compliance Overview |
| BSF-QMS-003 | Corrective Action and Nonconformity Procedure |
| BSF-IT-002 | Corporate Systems Access Guide |
