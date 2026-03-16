# Data Card — HRDataset_v14

**Project:** AttritionIQ

---

## 1. Source

| Attribute    | Value                                             |
| ------------ | ------------------------------------------------- |
| Dataset name | IBM HR Analytics Employee Attrition & Performance |
| File         | HRDataset_v14.csv                                 |
| Origin       | Kaggle — publicly available research dataset     |
| License      | CC0 — Public Domain                              |
| Records      | 311 employees                                     |
| Features     | 36 columns                                        |
| Format       | CSV, UTF-8                                        |

This dataset was originally published to support research in HR analytics and
people management. It represents a single US-based organization and was designed
to illustrate common attrition patterns, not to be representative of any
particular industry or geography.

---

## 2. Why This Dataset

The dataset was selected for three reasons:

1. It contains the behavioral and organizational signals most relevant to
   voluntary attrition prediction: engagement scores, satisfaction ratings,
   absenteeism, and compensation data.
2. It includes realistic class imbalance (~33% attrition), which reflects
   real-world HR conditions and tests the model's handling of minority-class
   prediction.
3. It is publicly licensed and contains no real personal data, making it
   appropriate for a demonstration system built around GDPR compliance.

---

## 3. GDPR Processing

The following transformations are applied before any data is used for training
or inference. The raw CSV never reaches the model.

**Step 1 — Direct identifiers removed:**

| Column        | Reason                                    |
| ------------- | ----------------------------------------- |
| Employee_Name | Full name — direct personal identifier   |
| DOB           | Date of birth — sensitive personal data  |
| Zip           | Postal code — location quasi-identifier  |
| State         | US state — location quasi-identifier     |
| ManagerName   | Full name — indirect personal identifier |

**Step 2 — Protected characteristics excluded:**

| Column                                    | Reason                   |
| ----------------------------------------- | ------------------------ |
| Sex / GenderID                            | Protected characteristic |
| RaceDesc                                  | Protected characteristic |
| HispanicLatino                            | Protected characteristic |
| MarriedID / MaritalStatusID / MaritalDesc | Protected characteristic |
| CitizenDesc                               | Nationality — protected |

These columns are not used as model features under any circumstances.
Their removal is enforced in `preprocessing.py` before the DataFrame
is passed to the training pipeline.

**Step 3 — ID anonymization:**
`EmpID` is replaced by a 12-character SHA-256 hash (`anon_id`). The original
ID is discarded. The hash is one-way and cannot be reversed to identify
an individual.

**Step 4 — Date engineering:**
`DateofHire`, `DateofTermination`, and `LastPerformanceReview_Date` are
converted to numeric features (`TenureDays`, `DaysSinceLastReview`).
The raw dates are then discarded.

---

## 4. Features Used in the Model

| Feature              | Type    | Range | Description                           |
| -------------------- | ------- | ----- | ------------------------------------- |
| EngagementSurvey     | Float   | 0–5  | Annual engagement survey score        |
| EmpSatisfaction      | Int     | 1–5  | Self-reported satisfaction            |
| Absences             | Int     | 0–n  | Absences in the review period         |
| Salary               | Int     | > 0   | Annual compensation                   |
| DaysLateLast30       | Int     | 0–30 | Lateness incidents                    |
| SpecialProjectsCount | Int     | 0–n  | Projects beyond standard scope        |
| PerfScoreID          | Int     | 1–4  | Performance rating (1=PIP, 4=Exceeds) |
| EmpStatusID          | Int     | 1–5  | Employment status code                |
| Department           | Encoded | —    | Department (label-encoded)            |
| Position             | Encoded | —    | Job title (label-encoded)             |
| RecruitmentSource    | Encoded | —    | Recruitment channel                   |
| TenureDays           | Derived | > 0   | Days from hire to reference date      |
| DaysSinceLastReview  | Derived | > 0   | Days since last review                |

---

## 5. Target Variable

| Column | Type   | Values                                      |
| ------ | ------ | ------------------------------------------- |
| Termd  | Binary | 1 = left the organization, 0 = still active |

**Class distribution:** ~67% active (0), ~33% terminated (1).

Note: `Termd=1` includes both voluntary resignations and involuntary
terminations. The dataset does not provide a clean separation between
the two. This is a known limitation of the target variable.

---

## 6. Known Limitations

- **Single organization, single country.** The data reflects one US company.
  Results may not transfer to organizations in different industries,
  geographies, or regulatory environments.
- **Static snapshot.** There is no temporal dimension. The model cannot
  detect trends over time or flag employees whose situation is rapidly
  changing.
- **Small sample.** Some departments and position categories contain
  fewer than 10 employees. Model performance on these subgroups is
  unreliable.
- **Mixed termination reasons.** Voluntary and involuntary exits are
  conflated in the target variable, which introduces label noise for a
  retention-focused use case.

---

## 7. Permitted and Prohibited Uses

| Use                                                            | Status          |
| -------------------------------------------------------------- | --------------- |
| Attrition risk scoring for HR decision support                 | Permitted       |
| HR trend analysis and department benchmarking                  | Permitted       |
| SHAP-based explanation of individual risk profiles             | Permitted       |
| Automated employment decisions of any kind                     | Prohibited      |
| Salary negotiation or performance management leverage          | Prohibited      |
| Sharing individual risk scores outside the HR team             | Prohibited      |
| Use in a real organization without retraining on internal data | Not recommended |
