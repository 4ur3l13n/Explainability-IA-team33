# AttritionIQ - Conceptual SaaS Offering

This document outlines the value proposition, customer journey, cybersecurity and GDPR aspects, pricing, roadmap, constraints, and deployment plan for a SaaS turnover prediction solution, based on the existing local prototype.

## Objectives
- Predict employee turnover using an explainable machine learning model.
- Protect PII (Personally Identifiable Information) by processing sensitive data locally on the client's premises.
- Provide anonymized SaaS dashboards to help IT/HR departments prioritize actions.

## Scope
- **In scope:** Local pipeline (ingestion, preprocessing, training), features + hash export, SaaS monitoring, GDPR/NIS2 compliance, EU data residency architecture.
- **Out of scope (V1):** Storing PII in the cloud, native integration with HRIS (Human Resources Information Systems), direct employee identification, use of non-hashed data.

## Instructions
### Prerequisites (2-day local MVP)
- Python 3.10+ installed (or version 3.11). 
- Docker (optional for containers) or local venv environment.
- Access to the sample CSV dataset (`data/HRDataset_v14.csv` file provided in this repository).
- Internet connection to install dependencies.

### Installation
1. Clone the repository:
   - `git clone <repo-url>`
   - `cd Explainability-IA-team33`
2. Create a Python virtual environment:
   - `python -m venv .venv`
   - `source .venv/Scripts/activate` (Windows) or `source .venv/bin/activate` (Linux/Mac)
3. Install dependencies:
   - `pip install -r backend/requirements.txt`

### Execution
- To run ingestion and train the local model:
  - `python backend/main.py` (or `python backend/model/train.py` depending on implementation).
- To serve a local dashboard (if applicable, e.g., Streamlit):
  - `streamlit run frontend/src/App.jsx` or `python backend/app.py`.
- To run with the file .sh:
  - `./start.sh`

On first launch, the backend runs the GDPR pipeline and trains the model
automatically (~60 seconds). Once ready:

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs


├── backend/
│   ├── data/preprocessing.py     GDPR anonymization pipeline
│   ├── model/train.py            Logistic Regression training + bias audit
│   ├── model/explain.py          SHAP explanations + HR recommendations
│   └── main.py                   FastAPI application
├── frontend/
│   └── src/pages/
│       ├── Dashboard.jsx         KPIs, risk distribution, feature importance
│       ├── EmployeeTable.jsx     Filterable risk table
│       └── ExplainView.jsx       SHAP waterfall + recommended actions
├── docs/
│   ├── model_card.md
│   └── data_card.md
├── data/                         Place HRDataset_v14.csv here
├── docker-compose.yml
└── start.sh


| Member        | Role                                                  |
| ------------- | ----------------------------------------------------- |
| Luka G.       | ML Engineering — model training, SHAP integration    |
| Hugo T.       | ML Engineering — EDA, bias audit, model card         |
| Taha I.       | Backend — FastAPI, security, input validation        |
| Aurélien KJ. | Frontend — React dashboard, data visualization       |
| Roman S.      | DevOps / Data — Docker, GDPR pipeline, documentation |

---

*TrustedAI Hackathon — Capgemini × ESILV, March 2026*

HR Data (CSV)
  	  │
   	 ▼
GDPR Preprocessor         — removes PII, hashes IDs, drops protected attributes
  	  │
	 ▼
Logistic Regression       — calibrated probabilities, interpretable coefficients
---

## 1) Persona Overview

### 1.1 Our Company (AttritionIQ)
- **Positioning:** SaaS solution for turnover prediction + HR analytics.
- **Target Audience:** SMEs/Mid-caps (200 - 5,000 employees), high-turnover industries (logistics, healthcare, finance, manufacturing, services), France/EU.
- **DNA:** Privacy-first, confidentiality, GDPR compliance, local processing of sensitive data.

### 1.2 Target Customer
- HR + Data Science + IT stakeholders facing staff retention challenges.
- **Objective:** Predict and reduce attrition, increase well-being at work, maintain loyalty values within the client company.
- **Needs:** Control over sensitive data, explainable model, GDPR compliance.

---

## 2) User Journey (Standard Process)

1. Initial qualification via sales contact.
2. Technical and compliance audit (available data, variables, sensitivity).
3. Local POC on the client side (On-premise infrastructure):
   - Dataset ingestion.
   - Preprocessing + model training.
   - Export of model features + employee hash.
4. Transmission to SaaS via secure channel (TLS, encryption, signed protocol).
5. Exploitation within the SaaS platform: dashboards, scoring, alerts.
6. Production deployment and monitoring (O&M, support, monthly KPIs).

---

## 3) Data Architecture and Anonymization

- Local processing of raw data.
- Authorized export: business variables relevant to the model, pseudonymized identifiers (SHA-256 hashes + salt).
- Strict prohibition on sending PII (first name, last name, SSN, email, etc.).
- Audit and logs: recording of all transformation/transfer operations.

### 3.1 Legal Framework and Local Processing (In-Memory)

Although the AttritionIQ SaaS platform does not store any Personally Identifiable Information (PII), the local ingestion and hashing of raw data constitutes **personal data processing** under Article 4 of the GDPR. Our *Privacy by Design* architecture strictly meets these requirements:

* **Role Distribution:** The Client remains the **Data Controller** of the HR data. The AttritionIQ local tool technically acts as the **Data Processor**.
* **Data Minimization (Art. 5):** The local script performs drastic filtering. It only loads configured columns into Random Access Memory (RAM). Any data read that falls outside the strict scope of the predictive model is ignored and immediately purged from memory.
* **Security of Ephemeral Processing (Art. 32):** Pseudonymization (SHA-256 Hash + Salt) is performed on the fly on the client's server. No unencrypted data is written to disk during this transition process.
* **Lawful Basis (Art. 6):** The solution's deployment is based on the company's **legitimate interest** (prevention of psychosocial risks, workforce retention, improvement of working conditions) or the prior **consent** of employees, in accordance with the client's record of processing activities.

**AttritionIQ** is an explainable AI tool built for HR teams to detect, understand,
and act on employee attrition risk — before it happens.

---


Employee turnover is one of the most expensive and underestimated challenges in HR.
Replacing a single employee costs between 50% and 200% of their annual salary when
accounting for recruitment, onboarding, and lost productivity. Most organizations
react to resignations after the fact, with no systematic way to identify who is at
risk, why, or what to do about it.

Existing HR tools track what happened. AttritionIQ predicts what will happen next.

---


AttritionIQ addresses three questions HR managers face every quarter:

- **Who is at risk?** — A ranked list of employees by attrition probability,
  updated from live HR data.
- **Why are they at risk?** — A per-employee SHAP explanation showing which
  factors drive the prediction: low engagement, absenteeism, compensation gap, etc.
- **What should we do?** — Prioritized, actionable HR recommendations tied
  directly to each employee's risk drivers.

By shifting HR from reactive to predictive, AttritionIQ reduces turnover costs,
improves retention strategy, and gives HR business partners a data-backed tool
for conversations with management.

---


This project was built with compliance and ethics at the center, not as an afterthought.

**GDPR compliance:**
All personally identifiable information (name, date of birth, ZIP code) is removed
before any data reaches the model. Employees are identified only by a one-way hashed
anonymous ID. No data leaves the local environment.

**Anti-discrimination:**
Protected attributes — gender, race, marital status, citizenship — are explicitly
excluded from the model. The system predicts attrition from behavioral and
organizational signals only.

**Human-in-the-loop:**
Every prediction screen carries a mandatory disclaimer. AttritionIQ is a
decision-support tool. No employment decision should be made on its output alone.

**Bias audit:**
Model performance is evaluated across performance score subgroups to detect
differential accuracy. Results are exposed via the `/metrics` endpoint.
---

## 4) Geographic Scope and Regulations

### Priority Zone
- France + EU.
- **Advantages:** GDPR, clear regulations, a market that demands data protection.

### Key Regulations
- GDPR (data minimization, privacy by design, DPIA).
- NIS2, ISO 27001, CNIL, LPM, data residency (EU-only).
- Beware of the Cloud Act: avoid direct data storage in the US. Standard Contractual Clauses (SCCs) required if transferring outside the EU.



SHAP LinearExplainer    — per-employee feature contribution scores
	│
	▼
FastAPI Backend           — secured endpoints, input validation, API key auth
	│
	▼
**React Frontend            — dashboard, risk table, SHAP waterfall, HR actions**


All services run locally via Docker Compose. Nothing is sent to external APIs.

---

## 5) Cybersecurity Focus

- **IAM:** MFA, RBAC, least privilege.
- **Encryption:** AES-256 at rest, TLS 1.2+ in transit.
- **Processes:** Pentesting, regular vulnerability assessments, SOC.
- **Collection:** Only anonymized data collected for global analysis.

---

## 6) Methodology / Compliance by Country

- **France:** DPO involvement, CNIL, record of processing activities, HR charter.
- **Germany:** BDSG + Datenschutz-Folgenabschätzung (DPIA).
- **Switzerland/UK:** Derived local rules + specific insurances.
- **Standard Cadence:** Inventory, classification, pseudo/anonymization, audit, governance.

---

## 7) Development Objectives

### MVP (2-day local prototype)
- CSV ingestion + preprocessing.
- Predictive model (XGBoost/LightGBM).
- Minimal export module (features + employee_hash).
- Basic local dashboard.

### V1 (SaaS)
- Client onboarding.
- Multi-tenant or single-tenant architecture with data residency.
- Secure submission API (HTTPS + auth token).
- Analytics database.
- Explainability module (SHAP-like).

### V2
- Multi-client anonymized benchmarks.
- HR recommendations and action plans.
- Real-time monitoring, alerting, incident management.

---

## 8) Commercial / Operational Roadmap

1. **Pre-sales:** Demo, RFI/RFP, workshop.
2. **Contracting:** NDA, SLA, GDPR text clauses, warranties.
3. **Installation:** Deployment / configuration (EU cloud, or hybrid local/SaaS mode).
4. **Training** + runbook.
5. **Go-Live / Production**.
6. **Support, monitoring, and evolution**.

---

## 9) Pricing

### Initial Setup Fees
- 15,000 - 25,000 EUR (audit, configuration, training, 3 months of onboarding support).

### Annual SaaS License
- **Standard Pack:** 8,000 EUR/year + 1 EUR/employee/month (200-2,000 employees).
- **Advanced Pack:** 15,000 EUR/year + 1.5 EUR/employee/month (recommendations, advanced monitoring).
- **Cybersecurity Option:** 5,000 EUR/year (audit, compliance, reporting).
- **Premium 24/7 Support:** 2,000 EUR/month.
- **Quarterly Model Retraining:** 2,000 EUR/quarter.

---

## 10) Key Differentiators

- Sensitive data remains with the client; only pseudo/anonymized data goes external.
- Privacy by design architecture.
- GDPR compliance + security guidance and support.
- Speed of MVP (2 days) leading to SaaS production (3-6 months).

---

## 11) Constraints

- Data quality on the client side.
- Risks of re-identification despite pseudonymization (must be managed contractually).
- Requires a DPO and a business sponsor on the client side.
- Limitations if clients enforce non-EU data localization.
- Local simulation does not yet cover all the requirements of a multi-tenant SaaS production environment.

---

## 12) Key Messaging

- "We do not touch employees' personal data."
- "Cyber strategy first, code second."
- "No direct Cloud Act storage for the EU offering."
- "Process: Sales → RFP → Deployment → Monitoring."
- "Local prototype available in 2 days, full SaaS in 3-6 months."

---

## 13) Appendices

- Proposed architecture (local + SaaS).
- Data flow diagram (hashing + non-PII export).
- List of variables strictly prohibited from export.
- Sample scale-up plan.

---

## 14) Suggested Next Steps

1. Detailed technical document (data pipeline, APIs, standards).
2. Security & compliance specifications (Cahier des charges).
3. Functional mockups (front-end + back-end).
4. Legal review (GDPR/Cloud Act).
5. Pilot client POC.