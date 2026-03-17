"""
explain.py — SHAP LinearExplainer for Logistic Regression.

Key fixes:
  - Background = zero vector (= mean of StandardScaled data, mathematically correct)
  - expected_value = model probability on mean input (in [0,1], not log-odds)
  - SHAP values are in log-odds contribution space → used for direction only
"""

import os
import pickle
import json
import numpy as np
import pandas as pd
import shap

BASE_DIR = os.path.dirname(__file__)
ARTIFACTS_DIR = os.environ.get("ARTIFACTS_DIR", os.path.join(BASE_DIR, "../data"))
MODEL_PATH = os.path.join(ARTIFACTS_DIR, "xgboost_model.pkl")
SCALER_PATH = os.path.join(ARTIFACTS_DIR, "scaler.pkl")
FEATURES_PATH = os.path.join(ARTIFACTS_DIR, "features.json")


def load_artifacts():
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
    with open(SCALER_PATH, "rb") as f:
        scaler = pickle.load(f)
    with open(FEATURES_PATH, "r") as f:
        features = json.load(f)
    return model, scaler, features


def get_local_explanation(employee_features: dict) -> dict:
    model, scaler, features = load_artifacts()

    X = pd.DataFrame([{f: employee_features.get(f, 0) for f in features}])
    X_scaled = scaler.transform(X)

    risk_score = float(model.predict_proba(X_scaled)[0][1])
    prediction = int(model.predict(X_scaled)[0])

    n_features = X_scaled.shape[1]
    background = np.zeros((1, n_features))

    explainer = shap.LinearExplainer(
        model, background, feature_perturbation="interventional"
    )
    sv = explainer.shap_values(X_scaled)
    if isinstance(sv, list):
        sv = sv[1]
    sv = np.array(sv).flatten()

    expected_prob = float(model.predict_proba(background)[0][1])

    shap_list = [
        {
            "feature": features[i],
            "value": float(X.iloc[0][features[i]]),
            "shap": float(sv[i]),
        }
        for i in range(len(features))
    ]
    shap_list.sort(key=lambda x: abs(x["shap"]), reverse=True)

    top_risk = [s["feature"] for s in shap_list if s["shap"] > 0][:3]
    top_protective = [s["feature"] for s in shap_list if s["shap"] < 0][:3]

    return {
        "risk_score": round(risk_score, 4),
        "prediction": prediction,
        "expected_value": round(expected_prob, 4),
        "shap_values": shap_list,
        "top_risk_factors": top_risk,
        "top_protective_factors": top_protective,
    }


def get_global_importance(df_processed_path: str) -> dict:
    model, scaler, features = load_artifacts()

    df = pd.read_csv(df_processed_path)
    X = df[[f for f in features if f in df.columns]].fillna(0)
    X_scaled = scaler.transform(X)
    n_features = X_scaled.shape[1]
    background = np.zeros((1, n_features))

    explainer = shap.LinearExplainer(
        model, background, feature_perturbation="interventional"
    )
    sv = explainer.shap_values(X_scaled)
    if isinstance(sv, list):
        sv = sv[1]
    sv = np.array(sv)

    mean_abs = np.abs(sv).mean(axis=0)
    mean_signed = sv.mean(axis=0)

    importance = sorted(
        [
            {
                "feature": features[i],
                "mean_abs_shap": round(float(mean_abs[i]), 4),
                "mean_signed_shap": round(float(mean_signed[i]), 4),
                "direction": "risk" if mean_signed[i] > 0 else "protective",
            }
            for i in range(len(features))
        ],
        key=lambda x: x["mean_abs_shap"],
        reverse=True,
    )
    return {"importance": importance[:15]}


def recommend_actions(shap_explanation: dict) -> list:
    RECOMMENDATIONS = {
        "EngagementSurvey": {
            "title": "Low Engagement Score",
            "action": "Schedule 1:1 meeting to identify blockers. Consider internal mobility or new project assignment.",
            "priority": "High",
        },
        "EmpSatisfaction": {
            "title": "Low Employee Satisfaction",
            "action": "Conduct anonymous pulse survey. Review compensation vs. market benchmark.",
            "priority": "High",
        },
        "Absences": {
            "title": "High Absenteeism",
            "action": "Initiate supportive conversation. Check for burnout or personal issues. Review workload.",
            "priority": "High",
        },
        "Salary": {
            "title": "Below-Market Salary",
            "action": "Review compensation band. Consider merit increase or retention bonus.",
            "priority": "Medium",
        },
        "DaysLateLast30": {
            "title": "Frequent Lateness",
            "action": "Explore flexible working arrangements or remote work options.",
            "priority": "Medium",
        },
        "SpecialProjectsCount": {
            "title": "Lack of Challenging Projects",
            "action": "Assign to cross-functional project. Discuss career development path.",
            "priority": "Medium",
        },
        "TenureDays": {
            "title": "At Critical Tenure Milestone",
            "action": "Proactive retention check-in. Offer mentoring or senior responsibilities.",
            "priority": "Low",
        },
    }
    return [
        RECOMMENDATIONS[f]
        for f in shap_explanation.get("top_risk_factors", [])
        if f in RECOMMENDATIONS
    ]
