# BRD Schema (Descriptive Draft)

This schema is derived from the two BRD samples provided. It defines a structured JSON output for the BRD generator and describes what each field should contain.

- All fields marked REQUIRED must be present.
- All list fields default to empty arrays if not available.
- Use concise, factual content. Avoid marketing language.
- Dates should be ISO 8601 (YYYY-MM-DD) where possible.

---

## 1) Document Metadata

### 1.1 `document_info` (REQUIRED)

- `title` (string, REQUIRED)
  - BRD title. Usually "Business Requirements Document (BRD)" or product-specific title.
- `version` (string, REQUIRED)
  - Document version identifier. Example: "1.0".
- `date` (string, REQUIRED)
  - Document creation date (ISO format).
- `engagement_model` (string, optional)
  - Commercial model if present (fixed bid, T&M, etc).

---

## 2) Executive Summary

### 2.1 `executive_summary` (REQUIRED)

- `overview` (string, REQUIRED)
  - High-level summary of the product, goals, and who it serves.
- `phases` (array of `phase`, optional)
  - Used when phased delivery is defined (Phase 1, Phase 2, etc).

`phase` object:
- `name` (string, REQUIRED)
  - Phase identifier (e.g., "Phase 1 - Buyer Treasury-Based Discounting").
- `summary` (string, REQUIRED)
  - What this phase delivers in plain language.
- `key_features` (array of strings, optional)
  - Bullet list of major features in that phase.

---

## 3) Business Objectives

### 3.1 `business_objectives` (array of strings, REQUIRED)

- Each item is a business goal/outcome (e.g., "Improve customer retention", "Enable multi-funder auctions").

---

## 4) Scope

### 4.1 `scope` (REQUIRED)

- `in_scope` (array of `scope_item`, REQUIRED)
  - Major in-scope modules, portals, or features.
- `out_of_scope` (array of strings, optional)
  - Explicit exclusions or non-goals.

`scope_item` object:
- `name` (string, REQUIRED)
  - The module/area name (e.g., "Vendor Web Portal", "Admin Portal").
- `details` (array of strings, optional)
  - Feature-level bullets inside that scope item.
- `phase` (string, optional)
  - Phase label if the item belongs to a specific phase.

---

## 5) Platforms / Applications

### 5.1 `platforms` (array of `platform`, REQUIRED)

`platform` object:
- `name` (string, REQUIRED)
  - Example: "Customer Mobile App", "Admin Portal".
- `type` (string, REQUIRED)
  - Example: "mobile", "web", "api".
- `notes` (string, optional)
  - Platform-specific details (iOS/Android, native/cross-platform).
- `phase` (string, optional)
  - Phase label if platform is phased.

---

## 6) User Personas

### 6.1 `personas` (array of `persona`, optional)

`persona` object:
- `name` (string, REQUIRED)
  - Persona label (e.g., "Vendor Uploader", "Wellness Customer").
- `description` (string, optional)
  - Short description of responsibilities or goals.

---

## 7) Functional Requirements

### 7.1 `functional_requirements` (array of `functional_group`, REQUIRED)

`functional_group` object:
- `name` (string, REQUIRED)
  - Example: "Vendor Web Portal", "User Authentication".
- `features` (array of strings, REQUIRED)
  - Feature-level requirements in bullet form.
- `phase` (string, optional)
  - Phase label if requirements are phased.

---

## 8) Non-Functional Requirements

### 8.1 `non_functional_requirements` (array of `nfr`, REQUIRED)

`nfr` object:
- `category` (string, REQUIRED)
  - Example: "Performance", "Security", "Scalability".
- `requirements` (array of strings, REQUIRED)
  - Specific NFR statements (latency, uptime, encryption, etc).

---

## 9) Technical Requirements

### 9.1 `technical_requirements` (array of `technical_group`, REQUIRED)

`technical_group` object:
- `category` (string, REQUIRED)
  - Example: "Integration", "Architecture".
- `requirements` (array of strings, REQUIRED)
  - Implementation-level constraints (APIs, platforms, hosting).

---

## 10) Integration Requirements

### 10.1 `integrations` (array of `integration`, optional)

`integration` object:
- `name` (string, REQUIRED)
  - System or service name (e.g., Zinoti, RazorpayX).
- `purpose` (string, optional)
  - Why the integration is required.
- `notes` (string, optional)
  - Any constraints, scope limitations, or phase notes.

---

## 11) Data Requirements

### 11.1 `data_requirements` (array of strings, optional)

- Data retention, backups, RPO/RTO, or data classifications.

---

## 12) UI/UX Requirements

### 12.1 `ui_ux_requirements` (array of strings, optional)

- UX principles, branding constraints, or accessibility requirements.

---

## 13) Reporting & Analytics

### 13.1 `reporting_analytics` (array of strings, optional)

- KPIs, dashboards, and reporting needs.

---

## 14) Support & Maintenance

### 14.1 `support_requirements` (array of strings, optional)

- Post go-live support terms, SLAs, or maintenance expectations.

---

## 15) Assumptions & Dependencies

### 15.1 `assumptions` (array of strings, optional)

- Assumptions about third-party systems, availability, or scope constraints.

### 15.2 `dependencies` (array of strings, optional)

- External dependencies that affect delivery (APIs, credentials, hardware).

---

## 16) Risks & Constraints

### 16.1 `risks` (array of strings, optional)

- Delivery risks, technical risks, or adoption risks.

### 16.2 `constraints` (array of strings, optional)

- Non-negotiable constraints (budget, timelines, compliance).

---

## 17) Change Control

### 17.1 `change_control` (array of strings, optional)

- Change request process or scope control rules.

---

## 18) Compliance & Security

### 18.1 `compliance_security` (array of strings, optional)

- Compliance or security obligations (data protection laws, health data).

---

# Proposed JSON Shape (Summary)

```
{
  "document_info": {
    "title": "...",
    "version": "1.0",
    "date": "YYYY-MM-DD",
    "engagement_model": "..."
  },
  "executive_summary": {
    "overview": "...",
    "phases": [
      {
        "name": "Phase 1",
        "summary": "...",
        "key_features": ["..."]
      }
    ]
  },
  "business_objectives": ["..."],
  "scope": {
    "in_scope": [
      {"name": "...", "details": ["..."], "phase": "..."}
    ],
    "out_of_scope": ["..."]
  },
  "platforms": [
    {"name": "...", "type": "mobile", "notes": "...", "phase": "..."}
  ],
  "personas": [
    {"name": "...", "description": "..."}
  ],
  "functional_requirements": [
    {"name": "...", "features": ["..."], "phase": "..."}
  ],
  "non_functional_requirements": [
    {"category": "Performance", "requirements": ["..."]}
  ],
  "technical_requirements": [
    {"category": "Integration", "requirements": ["..."]}
  ],
  "integrations": [
    {"name": "...", "purpose": "...", "notes": "..."}
  ],
  "data_requirements": ["..."],
  "ui_ux_requirements": ["..."],
  "reporting_analytics": ["..."],
  "support_requirements": ["..."],
  "assumptions": ["..."],
  "dependencies": ["..."],
  "risks": ["..."],
  "constraints": ["..."],
  "change_control": ["..."],
  "compliance_security": ["..."]
}
```
