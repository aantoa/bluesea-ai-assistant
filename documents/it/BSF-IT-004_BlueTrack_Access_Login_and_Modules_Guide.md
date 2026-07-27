# BlueSea Foods

Corporate Management System

[LOGO BSF]

---

## Document Information

- Document ID: BSF-IT-004
- Document Title: BlueTrack Access, Login and Modules Guide
- Department: Information Technology
- Process Owner: IT Manager
- Functional Approvers: Operations Manager; Quality Assurance Manager; Document Controller
- Version: 1.0
- Status: Draft for Review
- Effective Date: To be confirmed upon approval
- Review Date: Annual or after BlueTrack, access control, cybersecurity, or workflow change
- Confidentiality: Internal
- Language: English
- Keywords: BlueTrack, login, access, user account, password, session, MFA, SSO, module, dashboard, receiving module, cold chain module, temperature status, quality inspection module, traceability, access request, role profile, troubleshooting

---

## RAG Retrieval Note

This document is designed to answer explanatory questions about BlueTrack login, access, password rules, sessions, modules, temperature status, and user responsibilities. It should be prioritized over the full HTML user manual for short conceptual questions because it contains clean, direct Markdown sections optimized for retrieval.

---

## Purpose

This guide explains how authorized users access BlueTrack, how login and session rules work, what the main modules are used for, and what users should do when they cannot access the system or do not see the expected module.

It complements:

- BSF-IT-001 - BlueTrack User Manual
- BSF-IT-002 - Corporate Systems Access Guide
- BSF-IT-003 - Data Security and API Guidelines

---

## Quick Answers for AI Retrieval

### How is access to BlueTrack granted?

BlueTrack access is granted only after the user has a confirmed business need, manager approval, system owner approval where required, and IT implementation through the approved access request process. Users receive only the permissions needed for their role.

### How do users log in to BlueTrack?

Users open the approved BlueTrack URL from a company-managed browser or device, enter their corporate username and password, complete single sign-on or multi-factor authentication if requested, and confirm that their name, role, and assigned facility are correct after login.

### What are Password and Session Rules?

Password and Session Rules are the security requirements users must follow when accessing BlueTrack. Users must protect passwords, avoid saving passwords on shared workstations, lock the screen when away, log out after using shared terminals, and report suspicious login activity immediately to IT.

### What should a user do if they cannot log in?

The user should confirm credentials, retry MFA once if appropriate, check network or device restrictions, and contact IT support with the time of error, screenshot, browser or device, user name, and business impact. The user must not borrow another account.

### Why is a module missing after login?

A missing module usually means the user's role profile does not include that module. The user should ask the line manager to confirm whether access is required and submit an access change request. IT should not add access without approval.

### What is the Cold Chain Module?

The Cold Chain Module is the BlueTrack module used to record temperature readings, review temperature status, attach evidence, manage alerts, and link deviations to corrective action or Quality Assurance review.

---

## Access Principles

BlueTrack access follows these principles:

- least privilege;
- need to know;
- unique user identity;
- traceable approval;
- segregation of duties;
- timely removal during offboarding or role change;
- MFA or SSO where required;
- audit logging for critical actions.

Shared accounts are prohibited unless formally approved as a controlled service account with compensating controls.

---

## Standard Login Steps

1. Open the approved BlueTrack URL from a company-managed browser or approved device.
2. Enter the corporate username and password.
3. Complete SSO or MFA if prompted.
4. Confirm that the user name, role, site, and assigned facility are correct.
5. Review assigned tasks, pending approvals, alerts, and records on the dashboard.
6. Report incorrect role, wrong facility, missing module, or suspicious login activity to IT.

---

## Password and Session Rules

Users must:

- use only their own assigned account;
- keep passwords confidential;
- avoid saving passwords in browsers on shared workstations;
- change passwords immediately if compromise is suspected;
- complete MFA when required;
- lock the workstation before leaving it unattended;
- log out at the end of the shift or after using a shared terminal;
- avoid exporting or downloading restricted data unless approved;
- report unusual login activity, account lockout, suspected phishing, or unauthorized access immediately.

---

## Main BlueTrack Modules

| Module | Purpose | Typical Users |
|---|---|---|
| Dashboard | Shows assigned tasks, alerts, pending approvals, product holds, temperature alerts, and open corrective actions. | All authorized users |
| Receiving Module | Creates controlled records for incoming seafood, supplier, vessel, species, lot, temperature, documents, and inspection readiness. | Operations, Receiving, QA |
| Cold Chain Module | Records product and storage temperatures, status, evidence, alerts, deviations, and corrective actions. | Operations, Cold Storage, QA |
| Quality Inspection Module | Records inspection results, sensory checks, document review, product status, release, hold, rejection, or escalation. | QA, Food Safety |
| Traceability and Vessel Verification | Links lots to suppliers, authorized vessels, species records, certification status, and chain-of-custody evidence. | Traceability, Procurement, QA |
| Document Repository | Provides controlled access to approved documents and records. | Document Control, Process Owners, Auditors |
| Reports and Exports | Generates operational, traceability, temperature, audit, and KPI reports where the user has permission. | Management, QA, Operations |

---

## Temperature Status in BlueTrack

| Status | Meaning | User Action |
|---|---|---|
| Within Limit | Temperature is within the approved range for the product or location. | Continue monitoring. |
| Warning | Temperature is close to a limit, lacks evidence, or requires review. | Add comments/evidence and notify supervisor if needed. |
| Deviation | Temperature is outside the approved limit. | Notify supervisor and QA, link corrective action, and hold product when required. |
| Unknown | Temperature history cannot be confirmed. | Treat as potential deviation and escalate. |

BlueTrack may display a status, but Quality Assurance is responsible for product disposition when food safety, quality, legal, certification, or customer requirements may be affected.

---

## Access Request Minimum Fields

An access request should identify:

- user full name;
- employee or contractor ID;
- department;
- manager;
- site or facility;
- employment type;
- system requested;
- requested role or profile;
- business justification;
- start date;
- end date for temporary access;
- manager approval;
- system owner approval when required;
- training requirement if the role creates or approves controlled records.

---

## Troubleshooting

| Issue | Likely Cause | Required Action |
|---|---|---|
| Cannot log in | Password issue, MFA problem, expired access, network restriction, or locked account. | Contact IT with screenshot, time, user, device/browser, and business impact. |
| Missing module | Role profile does not include module. | Ask manager to confirm business need and submit access change request. |
| Wrong facility or role | Incorrect access profile or master data. | Report to IT and manager before entering controlled records. |
| Cannot submit record | Mandatory field or evidence missing. | Review highlighted fields and attach required evidence. |
| Temperature status seems incorrect | Wrong product, location, limit, or data entry. | Review entry and escalate to QA if unclear. |
| Export unavailable | User lacks export permission or data is restricted. | Request report through supervisor or process owner. |
| Suspicious login activity | Possible credential compromise or unauthorized access. | Report immediately to IT and manager. |

---

## User Responsibilities

BlueTrack users must:

- enter accurate, timely, and complete information;
- use only assigned personal accounts;
- protect credentials and MFA;
- follow document control and confidentiality rules;
- attach clear and relevant evidence;
- avoid bypassing holds, approvals, or mandatory fields;
- report suspected errors, unauthorized access, system malfunction, or data integrity issues;
- follow QA instructions when records affect product release, food safety, traceability, or certification.

---

## Related Documents

- BSF-IT-001 - BlueTrack User Manual
- BSF-IT-002 - Corporate Systems Access Guide
- BSF-IT-003 - Data Security and API Guidelines
- BSF-CORP-002 - Corporate Glossary
- BSF-CORP-006 - Frequently Asked Questions
- BSF-OPS-005 - Cold Chain and Freezing Procedure
- BSF-QMS-004 - Food Safety and HACCP Management Manual

---

## Revision History

| Version | Date | Description | Approved By |
|---|---:|---|---|
| 1.0 | 2026-07-24 | Initial RAG-oriented access, login, and modules guide prepared to complement the full BlueTrack user manual. | Pending |

