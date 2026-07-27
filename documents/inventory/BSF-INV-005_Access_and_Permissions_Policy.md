# BSF-INV-005 - Access and Permissions Policy

**BlueSea Foods | Document Control and RAG Readiness**

## Document Control

| Field | Value |
| --- | --- |
| Document Code | BSF-INV-005 |
| Document Title | Access and Permissions Policy |
| Version | 1.0 |
| Document Owner | Information Security Officer |
| Backup Owner | Knowledge Management Lead |
| Effective Date | 2026-07-21 |
| Source Review Format | Markdown |
| Target Export Format | Markdown / DOCX derivative when required |
| Confidentiality | Internal / Controlled |
| Review Cycle | Quarterly during RAG build; annual after stabilization |
| Status | Ready for review |
| Keywords | access control; permissions; confidentiality; role-based access; RAG security; document governance; least privilege; audit trail |

## Purpose

This policy defines how BlueSea Foods assigns, reviews, enforces, and audits access permissions for controlled documents and RAG-indexed knowledge sources. It ensures that employees, reviewers, managers, and technical users can retrieve the information they need while preventing unauthorized exposure of confidential operational, quality, HR, technology, and governance content.

## 1. Scope

This policy applies to all BlueSea Foods documents, registers, structured data files, training materials, HTML manuals, and metadata records listed in **BSF-INV-001 - Document Inventory** and prepared for ingestion under **BSF-INV-003 - Document Sources and Ingestion Plan**.

It covers source file access, RAG retrieval access, metadata visibility, role mapping, temporary access, exception handling, permission testing, review cycles, and audit evidence.

It does not replace human resources confidentiality rules, contractual nondisclosure obligations, regulatory reporting obligations, or system administration procedures. Where a stricter rule applies, the stricter rule must prevail.

## 2. Confidentiality

This document is classified as **Internal / Controlled**. It may be shared with approved BlueSea Foods personnel involved in document governance, information security, quality management, RAG implementation, audit preparation, and management review.

The policy itself may be visible to authorized internal users, but the access mappings, exception logs, security test results, and permission incident records must be handled as controlled records.

## 3. Access Principles

- **Least privilege:** users receive only the minimum access required for their role and business need.
- **Need-to-know:** access is based on work responsibility, not job title alone.
- **Role-based assignment:** permissions are mapped to approved roles or groups, not informal individual requests whenever avoidable.
- **Source and retrieval alignment:** a user must not retrieve through RAG what the same user is not allowed to access in the source repository.
- **Deny by default:** unresolved confidentiality, missing ownership, or unclear access group blocks release.
- **Traceable access:** every access decision must be traceable to an owner, approver, date, scope, and review cycle.
- **Periodic review:** access remains valid only while role, employment status, business need, and document classification remain valid.

## 4. Classification Model

| Classification | Description | RAG Handling |
| --- | --- | --- |
| Public Reference | Approved content that may be externally shared. | May be indexed in broad-access environments if source is approved. |
| Internal Use | Routine internal guidance without sensitive personal, commercial, or security details. | May be available to general BlueSea Foods internal users. |
| Internal / Controlled | Internal content requiring owner-controlled distribution and role awareness. | Available only to approved business roles or project groups. |
| Confidential - Internal | Sensitive content such as security details, access rules, audit findings, HR policy details, system controls, or commercial constraints. | Restricted to explicitly approved roles and tested for permission boundaries. |
| Restricted Record | Content with legal, privacy, contractual, disciplinary, investigation, or high-risk security implications. | Not indexed unless Information Security and Legal/Compliance approve a restricted implementation. |

## 5. Standard Access Groups

| Access Group | Typical Users | Approved Use |
| --- | --- | --- |
| All Internal Users | Employees and approved contractors with active accounts. | General corporate references, glossary, onboarding, and non-sensitive FAQs. |
| Document Control Team | Document controllers, knowledge management, and assigned document reviewers. | Inventory, ownership matrix, source readiness, metadata quality, and curation workflows. |
| Operations Team | Receiving, cold chain, inspection, warehouse, and operations supervisors. | Operational procedures, registers, species catalog, authorized vessel data, and receiving controls. |
| Quality and Compliance Team | Quality, certification, audit, HACCP, BRCGS, IFS, MSC, BASC, and SMETA coordinators. | QMS procedures, corrective action, compliance overviews, certification references, and quality records. |
| HR Team | HR, management reviewers, and approved onboarding owners. | HR procedures, onboarding material, employee FAQs, leave and benefits guidance. |
| HSE Team | Safety, health, environmental, emergency response, and facility supervisors. | Workplace safety, emergency response, incident controls, and HSE guidance. |
| IT and Security Team | System administrators, security reviewers, BlueTrack owners, and access approvers. | Access guides, system permissions, security controls, incidents, and technical configuration references. |
| Executive Reviewers | Approved senior management and audit sponsors. | Cross-area summaries, governance status, risks, KPIs, and controlled management review content. |

## 6. Permission Matrix by Document Area

| Business Area | Default Access Group | Higher Restriction Trigger |
| --- | --- | --- |
| Corporate | All Internal Users or Executive Reviewers | Organization structure, strategic information, or sensitive governance notes. |
| HR | HR Team with limited employee-facing excerpts | Personal data, benefits administration details, disciplinary content, or employee records. |
| HSE | HSE Team and relevant Operations Team | Incident investigations, regulatory findings, or emergency contacts with restricted distribution. |
| Operations | Operations Team and Quality Team | Supplier restrictions, commercial vessel data, deviation records, or facility-sensitive details. |
| Quality | Quality and Compliance Team | Audit findings, certification nonconformities, corrective actions, or regulatory evidence. |
| Technology | IT and Security Team | Access procedures, system roles, MFA exceptions, administrator permissions, or security incidents. |
| Document Control | Document Control Team and approved RAG Team | Metadata governance, curation scores, ingestion waves, source readiness, and exception logs. |

## 7. RAG Permission Requirements

| Requirement | Control Rule | Evidence |
| --- | --- | --- |
| Source authorization | Only documents listed or approved by the inventory owner may be indexed. | Inventory entry and owner approval. |
| Access label | Every indexed document must have confidentiality and access group metadata. | Metadata schema and access mapping. |
| Retrieval filtering | Search and answer generation must filter by user role before content is returned. | Permission test log. |
| Citation control | Citations must not reveal restricted document titles, paths, or sections to unauthorized users. | Redaction or refusal behavior test. |
| Metadata visibility | Metadata shown to users must match their access level. | Role-based UI/API checks. |
| Prompt response control | The assistant must refuse, limit, or redirect when requested content exceeds user access. | Denial test cases. |
| Audit logging | Restricted retrieval attempts, denials, overrides, and exceptions must be logged. | Access audit log. |

## 8. Access Request Workflow

| Step | Activity | Responsible Role | Output |
| ---: | --- | --- | --- |
| 1 | Submit access request with user, role, department, requested source group, and business justification. | Requester or manager | Access request record |
| 2 | Validate employment or contractor status and current business role. | HR or sponsoring manager | Eligibility confirmation |
| 3 | Confirm document classification and access group. | Document Owner | Source access decision |
| 4 | Review security risk and least-privilege scope. | Information Security Officer | Security approval or rejection |
| 5 | Apply access in source repository and RAG permission layer. | IT Administrator | Updated permissions |
| 6 | Test role-based retrieval for representative queries. | RAG Technical Lead | Permission test pass |
| 7 | Record decision, approver, access scope, expiry date if applicable, and review date. | Document Control Team | Access register entry |

## 9. Temporary and Emergency Access

| Access Type | Allowed Scenario | Maximum Duration | Required Control |
| --- | --- | ---: | --- |
| Temporary project access | User supports a defined document review, audit, implementation, or migration task. | 30 calendar days | Manager approval, owner approval, expiry date, and removal check. |
| Audit access | Internal or external audit requires controlled review of evidence. | Audit period plus closure window | Audit sponsor approval and restricted evidence room or access group. |
| Emergency operational access | Access is required to prevent safety, quality, continuity, or compliance impact. | 72 hours unless extended | Security approval, incident reference, post-access review. |
| Break-glass access | Urgent system recovery or critical incident response. | As short as operationally possible | Real-time logging, post-event review, and executive notification if sensitive content was accessed. |

Temporary access must be removed automatically or manually on the recorded expiry date. Extensions require a new approval or documented renewal.

## 10. Prohibited Practices

| Prohibited Practice | Reason |
| --- | --- |
| Sharing documents through personal drives, personal email, or uncontrolled messaging channels. | Breaks traceability and access control. |
| Indexing confidential sources without access metadata. | Exposes restricted information through retrieval. |
| Granting broad access because a user is senior. | Violates need-to-know and least privilege. |
| Reusing another user's account, token, or session. | Breaks accountability and audit trails. |
| Copying restricted answers into unrestricted documents or chats. | Circumvents RAG permissions. |
| Leaving temporary access open after the business need ends. | Increases exposure risk. |
| Ignoring stale or obsolete source warnings. | May lead to incorrect or outdated guidance. |

## 11. Permission Testing

| Test Type | Scenario | Expected Result |
| --- | --- | --- |
| Positive access | Authorized user asks a question covered by an approved source. | Correct answer, citation, and source metadata returned. |
| Negative access | Unauthorized user asks for confidential document content. | Access denied or limited response without sensitive detail. |
| Metadata leakage | Unauthorized user asks for hidden title, path, section, or owner note. | Restricted metadata is not exposed. |
| Cross-document query | User asks about a topic covered by both restricted and unrestricted sources. | Response uses only sources allowed for that user. |
| Role change | User moves department or project role. | Access updates within the required service window. |
| Revoked access | User leaves company, contractor engagement ends, or temporary access expires. | Source and RAG access removed. |
| Prompt injection attempt | User instructs the system to ignore permissions or reveal restricted content. | Request is refused and logged when required. |

## 12. Access Review Cycle

| Review Item | Frequency | Owner |
| --- | --- | --- |
| Active users with RAG access | Monthly during build; quarterly after stabilization | IT and Security Team |
| Confidential document access groups | Quarterly | Information Security Officer |
| Temporary access register | Weekly during active projects | Document Control Team |
| Document owner and backup owner validity | Quarterly | Knowledge Management Lead |
| Stale or obsolete indexed sources | Monthly | Document Control Team |
| Permission test regression suite | Each ingestion wave and major permission change | RAG Technical Lead |
| Executive exception review | Quarterly or upon high-risk exception | Executive Reviewer |

## 13. Exceptions

Exceptions may be approved only when a documented business need exists and the risk has been assessed. Each exception must include scope, justification, approver, compensating controls, expiry date, and review owner.

| Exception Type | Required Approver | Minimum Compensating Control |
| --- | --- | --- |
| Access outside standard group | Document Owner and Information Security Officer | Narrow scope, expiry date, and audit log review. |
| Extended temporary access | Manager, Document Owner, and Information Security Officer | Renewal record and weekly review. |
| Restricted record ingestion | Information Security Officer plus Legal/Compliance when applicable | Isolated index, strict role filter, denial tests, and executive sign-off. |
| Emergency break-glass access | IT/Security lead and executive notification when sensitive | Post-event review, incident record, and immediate revocation after use. |

## 14. Records and Evidence

| Record | Purpose | Responsible Role |
| --- | --- | --- |
| Access request register | Tracks request, requester, scope, decision, approver, and dates. | Document Control Team |
| Permission mapping file | Links document codes to allowed roles and access groups. | Information Security Officer |
| Temporary access log | Tracks temporary, audit, emergency, and break-glass access. | IT and Security Team |
| RAG permission test log | Shows role-based retrieval pass/fail results. | RAG Technical Lead |
| Access review evidence | Confirms periodic review and removal of unnecessary access. | Information Security Officer |
| Exception register | Records approved deviations and compensating controls. | Knowledge Management Lead |
| Permission incident record | Captures unauthorized access attempts, leakage, or control failures. | IT and Security Team |

## 15. Incident Response

| Incident Type | Immediate Action | Follow-Up |
| --- | --- | --- |
| Unauthorized document access | Revoke access, preserve logs, notify Information Security. | Root cause analysis and corrective action. |
| RAG returns restricted content to unauthorized user | Disable affected source or permission group, preserve interaction log. | Re-test filters, correct metadata, and document CAPA if required. |
| Incorrect broad permission assignment | Remove broad access and validate affected users. | Update role mapping and retrain approvers if needed. |
| Expired temporary access remains active | Remove access immediately. | Review automation or manual control failure. |
| Sensitive content copied outside approved channel | Contain distribution, identify recipients, and notify owner. | Remediation, awareness, and disciplinary/escalation review if required. |

## 16. KPIs

| KPI | Definition | Target |
| --- | --- | ---: |
| Permission metadata completeness | Indexed documents with completed confidentiality and access group fields. | 100% |
| Negative access test pass rate | Restricted-content test cases correctly denied or limited. | 100% |
| Temporary access closure rate | Temporary access removed by expiry date. | 100% |
| Access review completion | Scheduled access reviews completed on time. | 95% or higher |
| Permission incident closure time | Business days to close confirmed permission incidents. | 5 business days or less |
| Stale source restriction rate | Expired or obsolete restricted sources blocked or flagged. | 100% |

## 17. Internal References

| Code | Document |
| --- | --- |
| BSF-INV-001 | Document Inventory |
| BSF-INV-002 | Document Ownership Matrix |
| BSF-INV-003 | Document Sources and Ingestion Plan |
| BSF-INV-004 | Document Curation and Quality Criteria |
| BSF-IT-001 | BlueTrack User Manual |
| BSF-IT-002 | Corporate Systems Access Guide |
| BSF-QMS-003 | Corrective Action and Nonconformity Procedure |
| BSF-DOC-STD-001 | Corporate Document Standard |

## 18. Appendix A: Minimum Metadata for Permissioned Ingestion

| Field | Required Value |
| --- | --- |
| document_code | Official code from BSF-INV-001. |
| document_title | Official title from inventory and source file. |
| confidentiality | Approved classification. |
| access_group | Approved role group or restricted exception group. |
| owner | Accountable document owner. |
| backup_owner | Backup owner for continuity. |
| source_path | Stable source location or canonical pointer. |
| version | Approved document version. |
| review_date | Next required review date. |
| permission_test_status | Pass, fail, pending, or exception approved. |

## 19. Revision Notes

This Markdown file is the editable source for BSF-INV-005. Any DOCX or PDF version generated from it should be treated as a presentation/export copy unless formally promoted as the controlled source.
