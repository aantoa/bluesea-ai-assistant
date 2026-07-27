# BSF-INV-003 - Document Sources and Ingestion Plan

**BlueSea Foods | Document Control and RAG Readiness**

## Document Control

| Field | Value |
| --- | --- |
| Document Code | BSF-INV-003 |
| Document Title | Document Sources and Ingestion Plan |
| Version | 1.1 |
| Document Owner | Knowledge Management Lead |
| Effective Date | 2026-07-21 |
| Source Review Format | Markdown |
| Target Export Format | Markdown / DOCX derivative when required |
| Confidentiality | Internal / Controlled |
| Review Cycle | Quarterly during RAG build; annual after stabilization |
| Status | Ready for review |
| Keywords | document sources; ingestion plan; metadata; chunking; vector database; RAG; citations; access control; source validation; FAQ; quick answers; legal compliance; cold chain; BlueTrack |

## Purpose

This plan defines how BlueSea Foods documents are selected, validated, normalized, permissioned, chunked, indexed, tested, and released for retrieval-augmented generation use. It connects the document inventory and ownership matrix with the operational ingestion workflow.

## 1. Scope

This document applies to the internal BlueSea Foods knowledge base and RAG environment used to support controlled retrieval from corporate, HR, HSE, operations, quality, technology, and document control sources.

It covers source selection, document readiness, ingestion priority, metadata requirements, conversion rules, chunking rules, permission mapping, citation expectations, testing, release, and ongoing maintenance.

It does not approve uncontrolled public publication of documents, replacement of official procedures, or use of AI-generated answers as audit evidence without source verification.

## 2. Confidentiality

This plan is classified as **Internal / Controlled**. It contains information about document availability, ingestion sequencing, permission groups, metadata structure, and retrieval testing.

Access is limited to authorized document owners, RAG project members, system administrators, and approved management reviewers.

Documents classified as **Confidential - Internal** must remain restricted in the RAG layer. Retrieval responses must not expose content to users whose role does not match the document access profile in the inventory and access policy.

## 3. Source Baseline

The source baseline is taken from **BSF-INV-001 - Document Inventory** and **BSF-INV-002 - Document Ownership Matrix**. The ingestion plan must be updated whenever a document changes status, owner, confidentiality level, file format, review date, or source path.

| Metric | Value |
| --- | ---: |
| Total documents in inventory | 37 |
| Generated documents at current baseline | 31 |
| Planned documents at current baseline | 6 |
| Very high priority retrieval documents | 5 |
| High priority documents | To be maintained in BSF-INV-001 |
| Business areas covered | Corporate, Corporate Knowledge Management, Document Control, Finance, HR, HSE, Legal / Compliance, Operations, Quality, Technology |

## 4. Source Categories

| Source Category | Expected Format | RAG Use |
| --- | --- | --- |
| Controlled policy and procedure documents | DOCX or Markdown | Authoritative source for policies, procedures, responsibilities, definitions, and compliance language. |
| Operational registers and matrices | XLSX or CSV | Structured lookup for status, ownership, temperature records, vessel approval, review cycles, and action tracking. |
| Catalog and master data | JSON or CSV | Entity lookup, species mapping, controlled values, risk classification, and structured facts. |
| Training and user guidance | PPTX, HTML, or DOCX | Onboarding, employee assistance, process explanations, BlueTrack use, and practical help queries. |
| External standards references | Controlled citation only | Alignment context. Standards text must not be ingested unless licensed and approved. |

## 5. Ingestion Workflow

| Step | Activity | Minimum Control | Output |
| ---: | --- | --- | --- |
| 1 | Collect source | Document Controller confirms file location, current version, owner, and approved status. | Complete file package |
| 2 | Validate metadata | RAG team checks code, title, owner, access level, confidentiality, keywords, related documents, and review date. | Metadata pass/fail |
| 3 | Normalize content | Convert readable content to text-preserving ingestion format while keeping the source file as record of truth. | Normalized text and source pointer |
| 4 | Apply chunking | Split content by semantic section, table boundary, slide, worksheet, or structured record. | Chunk set with source anchors |
| 5 | Map permissions | Attach role-based access profile from inventory and permissions policy. | Permission labels |
| 6 | Index and embed | Load approved chunks into the retrieval index with stable document identifiers. | Indexed source |
| 7 | Test retrieval | Run representative questions, citation checks, permission tests, and conflict checks. | QA sign-off |
| 8 | Release and monitor | Publish to controlled RAG environment and track user feedback, failed retrievals, and stale-source warnings. | Released source |

## 6. Metadata Schema

| Field | Definition | Status | Ingestion Use |
| --- | --- | --- | --- |
| document_code | Unique document code such as BSF-QMS-003. | Required | Used for citations, filters, and document identity. |
| document_title | Official title in the inventory. | Required | Must match source file title and control table. |
| business_area | Corporate, HR, HSE, Operations, Quality, Technology, or Document Control. | Required | Used for search filtering and owner routing. |
| version | Approved version visible in the control table. | Required | Prevents outdated retrieval. |
| confidentiality | Internal Use or Confidential - Internal. | Required | Used for permissioning and response controls. |
| access_level | Allowed audience or role group. | Required | Mapped to system roles before indexing. |
| keywords | Semicolon or comma-separated retrieval terms. | Required | Improves recall and source discoverability. |
| source_path | Location or canonical pointer to the source file. | Required before release | Must be stable and traceable. |
| related_documents | Cross-referenced document codes. | Recommended | Supports multi-source responses. |
| review_date | Next review date. | Required | Triggers stale content warnings. |

## 7. Format-Specific Ingestion Rules

| Format | Ingestion Rule | Primary Examples |
| --- | --- | --- |
| DOCX | Extract by heading hierarchy; preserve tables as table blocks; keep control table metadata. | Policies, procedures, guides, compliance overviews. |
| Markdown | Parse headings and lists directly; preserve code blocks and tables; convert document control block into metadata. | FAQ, quick answers, curation criteria, access policies, source plans, Markdown companions for PDF/HTML sources. |
| PDF-listed documents delivered as DOCX | Use DOCX as the editable source of truth and export PDF only for locked distribution if needed. | Corporate references and controlled procedures. |
| XLSX | Treat each worksheet as a source unit; preserve formulas only in workbook; ingest values, sheet name, and row identifiers. | Registers, matrices, calendars, summaries. |
| CSV | Ingest row-wise with document-level metadata plus stable row identifiers. | Document inventory and authorized vessels. |
| JSON | Validate syntax; ingest object records with schema labels and keys. | Species catalog and master data. |
| PPTX | Chunk by slide; include slide title, speaker notes if approved, and visible text. | Quality induction and training content. |
| HTML | Chunk by section id; preserve navigation headings and tables. | BlueTrack user manual. |

## 8. Quality Gates Before Indexing

| Gate | Acceptance Criterion | Owner |
| --- | --- | --- |
| File integrity | File opens without error and is not blank. | Document Controller |
| Control metadata | Document code, title, owner, status, confidentiality, keywords, and review cycle are present. | Document Controller |
| Content completeness | Required sections exist and no placeholder text remains. | Document Owner |
| Authority check | Source is approved or clearly marked as draft/review. | Approver |
| Permission check | Access group matches confidentiality and business need. | Information Security Officer |
| Retrieval check | Test questions return correct source and citation. | RAG Team |
| Conflict check | New source does not contradict a newer approved document. | Knowledge Management Lead |

**Release rule:** A document may be indexed for production retrieval only when source integrity, metadata, ownership, confidentiality, and retrieval tests have passed. Draft or incomplete documents may be loaded only in a restricted test index.

## 9. Initial Ingestion Waves

| Wave | Documents | Objective |
| --- | --- | --- |
| Wave 1 - RAG foundation | BSF-INV-001, BSF-INV-002, BSF-INV-003, BSF-INV-004, BSF-INV-005 | Create governance layer, inventory, ownership, permissions, source quality rules and ingestion controls. |
| Wave 2 - Conceptual answer layer | BSF-CORP-002, BSF-CORP-006, BSF-QMS-005, BSF-OPS-005, BSF-IT-004, BSF-HR-004, BSF-LEGAL-001 | Prioritize clean Markdown sources that answer frequent conceptual questions before registers, charts or raw data. |
| Wave 3 - Operations core | BSF-OPS-001, BSF-OPS-002, BSF-OPS-003, BSF-OPS-004, BSF-QMS-004, BSF-IT-001 | Enable operational answers on receiving, cold chain, vessel authorization, species data, HACCP and BlueTrack workflows. |
| Wave 4 - HR, HSE, Finance and Compliance support | BSF-HR-001, BSF-HR-002, BSF-HR-003, BSF-HSE-001, BSF-HSE-002, BSF-FIN-001, BSF-COM-001 | Support employee onboarding, safety, emergency response, leave, benefits, reimbursement, communication and compliance questions. |
| Wave 5 - Corporate reference layer | BSF-CORP-001, BSF-CORP-003, BSF-CORP-004, BSF-CORP-005, BSF-DOC-STD-001 | Add corporate context, governance, organization routing, roadmap, knowledge map and document standard. |
| Wave 6 - Project control and continuous improvement | BSF-RAG-001, BSF-RAG-002 | Track RAG improvement actions. Keep these sources low priority for general employee answers. |

## 10. Retrieval Test Set

| Test Area | Example Question | Expected Behavior |
| --- | --- | --- |
| Document identity | Which document defines corrective actions for nonconformities? | BSF-QMS-003 must be cited. |
| Operational lookup | What must be checked before receiving seafood from an authorized vessel? | OPS receiving procedure plus vessel master data must be cited. |
| Permission behavior | Can all employees see confidential access guide details? | Answer must respect access restrictions from IT-002 and INV-005. |
| Structured source | What is the target temperature for a species in the catalog? | JSON catalog chunk must be retrieved with species identifier. |
| Cross-document reasoning | What documents support cold chain deviation management? | OPS-005, OPS-001, OPS-004, QMS-004/QMS-005 and HSE-002 should be linked. |
| Conceptual answer | What is HACCP? | CORP-006, CORP-002, QMS-004 and QMS-005 should be prioritized. |
| System help | How do I access and log in to BlueTrack? | IT-004 should be prioritized, with IT-001 and IT-002 as supporting sources. |
| Labor/legal support | What should I do if I have a workplace complaint or legal concern? | HR-004, HR-002, CORP-006 and LEGAL-001 should be cited according to topic. |
| Staleness warning | Is a document past review date? | System must warn and route to owner when review date has expired. |

## 11. Roles and Responsibilities

| Role | Responsibility |
| --- | --- |
| Knowledge Management Lead | Owns ingestion plan, coordinates waves, resolves source conflicts, and approves release readiness. |
| Document Control Specialist | Maintains inventory, validates metadata, confirms controlled versions, and tracks review dates. |
| Document Owner | Confirms content accuracy, business applicability, and completeness before ingestion. |
| Information Security Officer | Approves confidentiality labels, role mappings, and permission tests. |
| RAG Technical Lead | Runs extraction, chunking, indexing, retrieval tests, monitoring, and rollback when needed. |
| Quality Management Coordinator | Ensures certification-sensitive content aligns with QMS, HACCP, BRCGS, IFS, MSC, BASC, and SMETA commitments. |

## 12. Monitoring and Maintenance

- Review ingestion logs weekly during build phase and monthly after launch.
- Track unanswered questions, low-confidence retrieval, wrong citations, stale-source warnings, and permission denials.
- Update or remove indexed content within five business days after an approved source document changes.
- Run regression retrieval tests after every major indexing change or document wave.
- Maintain a rollback package for each ingestion wave, including source file list, metadata export, and index version.

## 13. Internal References

| Code | Document |
| --- | --- |
| BSF-INV-001 | Document Inventory |
| BSF-INV-002 | Document Ownership Matrix |
| BSF-INV-004 | Document Curation and Quality Criteria |
| BSF-INV-005 | Access and Permissions Policy |
| BSF-CORP-004 | Corporate Knowledge Map |
| BSF-DOC-STD-001 | Corporate Document Standard |
| BSF-IT-001 | BlueTrack User Manual |
| BSF-IT-002 | Corporate Systems Access Guide |
| BSF-IT-004 | BlueTrack Access Login and Modules Guide |
| BSF-LEGAL-001 | Data Privacy and Compliance Policy |
| BSF-OPS-005 | Cold Chain and Freezing Procedure |
| BSF-QMS-002 | Certification and Compliance Overview |
| BSF-QMS-003 | Corrective Action and Nonconformity Procedure |
| BSF-QMS-004 | Food Safety and HACCP Management Manual |
| BSF-QMS-005 | HACCP and Food Safety Quick Answers |

## 14. Appendix A: Area Coverage Snapshot

| Business Area | Documents in Inventory |
| --- | ---: |
| Corporate | 9 |
| Corporate Knowledge Management | 2 |
| Document Control | 5 |
| Finance | 1 |
| HR | 4 |
| HSE | 2 |
| Legal / Compliance | 1 |
| Operations | 5 |
| Quality and Certifications | 5 |
| Technology | 4 |

## 15. Revision Notes

This Markdown file is the editable source for BSF-INV-003. Any DOCX or PDF version generated from it should be treated as a presentation/export copy unless formally promoted as the controlled source.

| Version | Date | Description | Owner |
| --- | --- | --- | --- |
| 1.0 | 2026-07-21 | Initial ingestion plan based on 24-document planning baseline. | Knowledge Management Lead |
| 1.1 | 2026-07-24 | Updated inventory counts, ingestion waves, legal/compliance area and quick-answer sources after RAG document reinforcement. | Knowledge Management Lead |
