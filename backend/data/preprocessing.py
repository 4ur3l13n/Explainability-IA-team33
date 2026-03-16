"""
preprocessing.py
GDPR-compliant data pipeline for the HR Attrition dataset.
- Drops all Personally Identifiable Information (PII)
- Encodes categorical variables
- Outputs a clean, anonymized dataset ready for ML training
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import hashlib
import os

# ─────────────────────────────────────────────
# PII columns to drop entirely (GDPR Article 4)
# ─────────────────────────────────────────────
PII_COLUMNS = [
    "Employee_Name",  # Direct identifier
    "DOB",            # Date of birth
    "Zip",            # Location quasi-identifier
    "State",          # Location quasi-identifier
    "ManagerName",    # Indirect identifier
]

# ─────────────────────────────────────────────
# Sensitive/discriminatory columns NOT used as features
# (EU AI Act + ethical AI — cannot be used for predictions)
# ─────────────────────────────────────────────
SENSITIVE_COLUMNS = [
    "GenderID",
    "MarriedID",
    "MaritalStatusID",
    "HispanicLatino",
    "RaceDesc",
    "CitizenDesc",
    "Sex",
    "MaritalDesc",
]

# ─────────────────────────────────────────────
# Date columns to convert to tenure/age features
# ─────────────────────────────────────────────
DATE_COLUMNS = ["DateofHire", "DateofTermination", "LastPerformanceReview_Date"]


def anonymize_id(emp_id: int) -> str:
    """
    One-way hash of EmpID so no real ID is stored in outputs.
    """
    return hashlib.sha256(str(emp_id).encode()).hexdigest()[:12]


def compute_tenure_days(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert hire/termination dates to numeric tenure feature.
    """
    df["DateofHire"] = pd.to_datetime(df["DateofHire"], errors="coerce")
    df["DateofTermination"] = pd.to_datetime(df["DateofTermination"], errors="coerce")
    reference_date = pd.Timestamp("2023-01-01")

    df["TenureDays"] = (
        df["DateofTermination"].fillna(reference_date) - df["DateofHire"]
    ).dt.days

    df["DaysSinceLastReview"] = (
        reference_date
        - pd.to_datetime(df["LastPerformanceReview_Date"], errors="coerce")
    ).dt.days.fillna(-1)

    return df


def encode_categoricals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Label-encode remaining string columns that are model features.
    """
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
    return df


def load_and_clean(filepath: str) -> pd.DataFrame:
    """
    Full GDPR-compliant preprocessing pipeline.
    Returns anonymized DataFrame with:
      - 'anon_id': hashed identifier (for UI display only)
      - 'Termd': target variable (1 = left, 0 = active)
      - all engineered features
    """
    df = pd.read_csv(filepath)
    print(f"[INFO] Loaded {len(df)} rows, {df.shape[1]} columns")

    # 1. Hash EmpID before dropping PII
    df["anon_id"] = df["EmpID"].apply(anonymize_id)

    # 2. Drop PII
    df.drop(columns=PII_COLUMNS, inplace=True, errors="ignore")
    print(f"[GDPR] Dropped PII columns: {PII_COLUMNS}")

    # 3. Drop discriminatory/sensitive columns (not used as features)
    df.drop(columns=SENSITIVE_COLUMNS, inplace=True, errors="ignore")
    print(f"[ETHICS] Dropped sensitive columns: {SENSITIVE_COLUMNS}")

    # 4. Engineer date features
    df = compute_tenure_days(df)
    df.drop(columns=DATE_COLUMNS, inplace=True, errors="ignore")

    # 5. Drop raw ID columns no longer needed
    df.drop(columns=["EmpID", "PositionID", "DeptID", "ManagerID"], inplace=True, errors="ignore")

    # 6. Encode remaining categoricals
    # Keep anon_id separate, encode the rest
    anon_ids = df["anon_id"].copy()
    df.drop(columns=["anon_id"], inplace=True)
    df = encode_categoricals(df)
    df["anon_id"] = anon_ids

    # 7. Handle missing values
    df.fillna(df.median(numeric_only=True), inplace=True)

    print(f"[INFO] Clean dataset: {len(df)} rows, {df.shape[1]} columns")
    print(f"[INFO] Target distribution:\n{df['Termd'].value_counts()}")

    return df


def get_feature_columns(df: pd.DataFrame) -> list:
    """
    Returns list of feature columns (excludes target and anon_id).
    """
    exclude = ["Termd", "anon_id", "EmploymentStatus", "TermReason", "DateofTermination"]
    return [c for c in df.columns if c not in exclude]


if __name__ == "__main__":
    raw_path = os.environ.get("DATA_RAW_PATH", os.path.join(os.path.dirname(__file__), "../../data/HRDataset_v14.csv"))
    out_path = os.environ.get("DATA_PROCESSED_PATH", os.path.join(os.path.dirname(__file__), "../../data/processed.csv"))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    clean_df = load_and_clean(raw_path)
    clean_df.to_csv(out_path, index=False)
    print(f"[OK] Saved anonymized dataset to {out_path}")
