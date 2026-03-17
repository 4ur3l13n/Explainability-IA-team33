
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




SHAP LinearExplainer    — per-employee feature contribution scores
	│
	▼
FastAPI Backend           — secured endpoints, input validation, API key auth
	│
	▼
**React Frontend            — dashboard, risk table, SHAP waterfall, HR actions**


All services run locally via Docker Compose. Nothing is sent to external APIs.

---


**Prerequisites:** Docker Desktop, the HR dataset CSV.

```bash
git clone https://github.com/your-team/attrition-iq.git
cd attrition-iq
cp /path/to/HRDataset_v14.csv ./data/
chmod +x start.sh && ./start.sh
```

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

*TrustedAI Hackathon — Capgemini × ESILV, March 2025*

HR Data (CSV)
  	  │
   	 ▼
GDPR Preprocessor         — removes PII, hashes IDs, drops protected attributes
  	  │
	 ▼
Logistic Regression       — calibrated probabilities, interpretable coefficients
