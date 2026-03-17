"""
train.py
Logistic Regression for attrition prediction.
- Naturally well-calibrated probabilities (no extreme 0/1 scores)
- Ideal for small datasets (311 rows)
- L2 regularization via C parameter
- SHAP LinearExplainer for explanations
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import roc_auc_score, f1_score, brier_score_loss
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.utils.class_weight import compute_class_weight
import warnings

warnings.filterwarnings("ignore")


BASE_DIR = os.path.dirname(__file__)
ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", os.path.join(BASE_DIR, "../data"))
DATA_PATH = os.path.join(ARTIFACTS_DIR, "processed.csv")
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "xgboost_model.pkl")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler.pkl")
FEATURES_PATH = os.path.join(ARTIFACTS_DIR, "features.json")
METRICS_PATH = os.path.join(ARTIFACTS_DIR, "metrics.json")


def load_data():
    df = pd.read_csv(DATA_PATH)
    feature_cols = [
        c
        for c in df.columns
        if c not in ["Termd", "anon_id", "EmploymentStatus", "TermReason"]
    ]
    X = df[feature_cols]
    y = df["Termd"]
    return X, y, feature_cols, df


def train():
    print("[TRAIN] Loading processed data...")
    X, y, feature_cols, df = load_data()

    print(f"[TRAIN] Features ({len (feature_cols )}): {feature_cols }")
    print(f"[TRAIN] Class balance: {y .value_counts ().to_dict ()}")

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(
        C=0.1,
        class_weight="balanced",
        max_iter=1000,
        solver="lbfgs",
        random_state=42,
    )

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_results = cross_validate(
        model,
        X_scaled,
        y,
        cv=cv,
        scoring=["roc_auc", "f1", "accuracy"],
        return_train_score=False,
    )

    print("\n[CV RESULTS]")
    for metric, scores in cv_results.items():
        if metric.startswith("test_"):
            print(f"  {metric }: {scores .mean ():.3f} ± {scores .std ():.3f}")

    model.fit(X_scaled, y)

    proba = model.predict_proba(X_scaled)[:, 1]
    print(f"\n[PROBABILITY DISTRIBUTION]")
    for p in [10, 25, 50, 75, 90]:
        print(f"  p{p }: {np .percentile (proba ,p ):.3f}")
    print(f"  min: {proba .min ():.3f}  max: {proba .max ():.3f}")

    df_audit = df.copy()
    df_audit["pred"] = model.predict(X_scaled)
    df_audit["pred_proba"] = proba

    bias_report = {}
    if "PerfScoreID" in df_audit.columns:
        print("\n[BIAS AUDIT] by PerfScoreID:")
        for group, gdf in df_audit.groupby("PerfScoreID"):
            if len(gdf) > 5:
                f1 = f1_score(gdf["Termd"], gdf["pred"], zero_division=0)
                bias_report[f"PerfScore_{int (group )}"] = {
                    "n": len(gdf),
                    "attrition_rate": float(gdf["Termd"].mean()),
                    "avg_predicted_risk": round(float(gdf["pred_proba"].mean()), 3),
                    "f1": round(f1, 3),
                }
                print(
                    f"  PerfScore {int (group )}: n={len (gdf )}, "
                    f"actual={gdf ['Termd'].mean ():.1%}, "
                    f"predicted={gdf ['pred_proba'].mean ():.1%}"
                )

    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)

    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)

    with open(FEATURES_PATH, "w") as f:
        json.dump(feature_cols, f)

    brier = brier_score_loss(y, proba)
    metrics = {
        "model_type": "LogisticRegression",
        "auc_roc": round(float(cv_results["test_roc_auc"].mean()), 3),
        "f1": round(float(cv_results["test_f1"].mean()), 3),
        "accuracy": round(float(cv_results["test_accuracy"].mean()), 3),
        "brier_score": round(brier, 4),
        "prob_distribution": {
            f"p{p }": round(float(np.percentile(proba, p)), 3)
            for p in [10, 25, 50, 75, 90]
        },
        "bias_audit": bias_report,
    }
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)

    print(
        f"\n[OK] Model saved → AUC={metrics ['auc_roc']}, F1={metrics ['f1']}, Brier={brier :.4f}"
    )
    return model, scaler, feature_cols


if __name__ == "__main__":
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    train()
