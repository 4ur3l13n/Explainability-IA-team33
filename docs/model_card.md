# MODEL CARD - AttritionIQ Attrition Risk Classifier

**Project:** AttritionIQ
**Version:** 1.0 | **Date:** March 2025

---

## 1. Model Purpose

This model predicts the probability that an employee will voluntarily leave
the organization within the near term, based on anonymized behavioral and
organizational features.

It is designed to help HR Business Partners prioritize retention conversations
and interventions - not to make or inform employment decisions automatically.

**Input:** Anonymized employee feature vector (engagement, satisfaction, absences,
salary, tenure, performance score, etc.)

**Output:** A risk score between 0 and 1, a risk category (Low / Medium / High),
and a SHAP explanation of the top contributing factors.

---

## 2. Model Choice and Rationale

**Algorithm:** Logistic Regression (scikit-learn, L2 regularization, C=0.1)

Logistic Regression was selected over tree-based methods (XGBoost, Random Forest)
for three reasons specific to this use case:

- **Dataset size:** With 311 records, gradient boosting models tend to memorize
  training examples, producing overconfident predictions (scores near 0 or 1
  with little in between). Logistic Regression generalizes more reliably on
  small tabular datasets.
- **Calibration:** Logistic Regression produces naturally well-calibrated
  probabilities, meaning a score of 0.6 genuinely reflects ~60% likelihood.
  This is essential when the output is used to prioritize human conversations,
  not just classify.
- **Interpretability:** The linear decision boundary maps directly onto SHAP
  linear explanations, ensuring that the feature contributions shown to HR
  managers are mathematically consistent with how the model actually works.

**Class imbalance handling:** `class_weight='balanced'` - reweights the loss
function proportionally to class frequency without distorting the output
probability space.

---

## 3. Training Data

- **Source:** IBM HR Analytics Employee Attrition Dataset (HRDataset_v14.csv)
- **Records:** 311 employees, 36 raw features
- **Target:** `Termd` - 1 if the employee left, 0 if still active
- **Class split:** ~67% active, ~33% terminated

All data is preprocessed through the GDPR pipeline before training.
See `data_card.md` for full feature documentation.

---

## 4. Features Used

| Feature              | Type       | Description                             |
| -------------------- | ---------- | --------------------------------------- |
| EngagementSurvey     | Float 0-5  | Annual engagement survey score          |
| EmpSatisfaction      | Int 1-5    | Self-reported job satisfaction          |
| Absences             | Int        | Number of absences in the review period |
| Salary               | Int        | Annual compensation                     |
| DaysLateLast30       | Int        | Lateness incidents in the last 30 days  |
| SpecialProjectsCount | Int        | Projects beyond standard role scope     |
| PerfScoreID          | Int 1-4    | Performance rating                      |
| EmpStatusID          | Int        | Employment status code                  |
| Department           | Encoded    | Department (label-encoded)              |
| Position             | Encoded    | Job title (label-encoded)               |
| RecruitmentSource    | Encoded    | How the employee was recruited          |
| TenureDays           | Derived    | Days from hire date to reference date   |
| DaysSinceLastReview  | Derived    | Days since last performance review      |

**Excluded - protected characteristics (EU AI Act compliance):**
Sex, GenderID, RaceDesc, HispanicLatino, MarriedID, MaritalStatusID, CitizenDesc.

**Excluded - direct identifiers (GDPR compliance):**
Employee_Name, DOB, Zip, State, ManagerName.

---

## 5. Performance

All metrics are from 5-fold stratified cross-validation to prevent data leakage.

| Metric      | Score                                  |
| ----------- | -------------------------------------- |
| AUC-ROC     | See `/metrics` endpoint after training |
| F1 Score    | See `/metrics` endpoint after training |
| Accuracy    | See `/metrics` endpoint after training |
| Brier Score | See `/metrics` endpoint after training |

**Bias audit:** F1 and attrition rate are computed separately for each
PerfScoreID subgroup (1-4) to detect differential performance across
employee profiles. Results are logged to `metrics.json` at training time.

---

## 6. Limitations

- **Small dataset.** 311 records is sufficient for a proof of concept but
  insufficient for production deployment in a large organization. Performance
  metrics should be treated as indicative.
- **Static snapshot.** The model captures a point-in-time view. It has no
  knowledge of events that occurred after the training data was collected.
  Retraining on fresh data is required as HR conditions evolve.
- **US context.** The source dataset reflects a US company. Labor market
  dynamics, legal context, and cultural factors differ in Europe.
- **Voluntary vs. involuntary.** The `Termd` flag does not distinguish between
  voluntary resignations and involuntary terminations. This introduces noise
  for the specific use case of retention.

---

## 7. Risks and Mitigations

| Risk                              | Control                                                                              |
| --------------------------------- | ------------------------------------------------------------------------------------ |
| HR manager over-relies on score   | Mandatory human-in-the-loop disclaimer on every prediction screen                   |
| Model used to justify termination | System is scoped to retention support only - documented and surfaced in the UI      |
| Sensitive data exposure           | PII removed pre-training; no raw data accepted by the API                           |
| Adversarial or malformed input    | Pydantic strict validation with field-level range constraints                       |
| Score misread as certainty        | UI shows score as a probability range, not a binary verdict                         |

---

## 8. Energy and Compute

| Attribute      | Value                                  |
| -------------- | -------------------------------------- |
| Model size     | < 1 MB (serialized with pickle)        |
| Training time  | < 5 seconds on CPU (311 rows)          |
| Inference time | < 10 ms per prediction on CPU          |
| GPU required   | No                                     |
| Estimated CO2  | Negligible - CPU only, small dataset   |

---

## 9. Cybersecurity

| Measure           | Implementation                                                     |
| ----------------- | ------------------------------------------------------------------ |
| Authentication    | `X-API-Key` header required on all endpoints                       |
| Input validation  | Pydantic models with strict types and value ranges                 |
| PII rejection     | API accepts only numeric feature vectors - no names or identifiers |
| Secret management | API key stored in `.env`, excluded from version control            |
| CORS policy       | Restricted to `localhost:3000` in production configuration         |
