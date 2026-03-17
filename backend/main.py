"""
main.py - AttritionIQ FastAPI Backend
- Starts immediately (no blocking training at boot)
- Preprocessing + training run in background thread
- /health reports readiness status
- CORS open for local dev
"""

import os
import json
import threading
import pandas as pd
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Security
from fastapi.security.api_key import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from contextlib import asynccontextmanager


API_KEY = os.getenv("API_KEY", "dev-secret-change-in-prod")
API_KEY_NAME = "X-API-Key"
DATA_RAW_PATH = os.getenv("DATA_RAW_PATH", "./rawdata/HRDataset_v14.csv")
DATA_PROCESSED_PATH = os.getenv("DATA_PROCESSED_PATH", "./artifacts/processed.csv")
ARTIFACTS_DIR = os.getenv("ARTIFACTS_DIR", "./artifacts")

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


app_state = {
    "ready": False,
    "status": "starting",
    "error": None,
}


def run_pipeline():
    """Runs preprocessing + training in a background thread."""
    try:
        from data.preprocessing import load_and_clean

        os.makedirs(ARTIFACTS_DIR, exist_ok=True)

        if not os.path.exists(DATA_PROCESSED_PATH):
            app_state["status"] = "preprocessing"
            print("[PIPELINE] Running GDPR preprocessing...")
            df = load_and_clean(DATA_RAW_PATH)
            df.to_csv(DATA_PROCESSED_PATH, index=False)
            print("[PIPELINE] Preprocessing done.")
        else:
            print("[PIPELINE] Processed data already exists, skipping preprocessing.")

        model_path = os.path.join(ARTIFACTS_DIR, "xgboost_model.pkl")
        if not os.path.exists(model_path):
            app_state["status"] = "training"
            print("[PIPELINE] Training model...")
            from model.train import train

            train()
            print("[PIPELINE] Training done.")
        else:
            print("[PIPELINE] Model already exists, skipping training.")

        app_state["ready"] = True
        app_state["status"] = "ready"
        print("[PIPELINE] Backend ready.")

    except Exception as e:
        app_state["status"] = "error"
        app_state["error"] = str(e)
        print(f"[PIPELINE] Error: {e }")
        import traceback

        traceback.print_exc()


@asynccontextmanager
async def lifespan(app: FastAPI):

    t = threading.Thread(target=run_pipeline, daemon=True)
    t.start()
    yield


app = FastAPI(
    title="AttritionIQ API",
    description="Explainable AI for HR Attrition Prediction",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key


def require_ready():
    if not app_state["ready"]:
        raise HTTPException(
            status_code=503,
            detail=f"Model not ready yet — status: {app_state ['status']}. "
            f"{'Error: '+app_state ['error']if app_state ['error']else 'Please wait ~60s for training to complete.'}",
        )


class EmployeeInput(BaseModel):
    EngagementSurvey: float = Field(..., ge=0.0, le=5.0)
    EmpSatisfaction: int = Field(..., ge=1, le=5)
    Absences: int = Field(..., ge=0, le=100)
    Salary: int = Field(..., ge=0, le=500000)
    DaysLateLast30: int = Field(..., ge=0, le=30)
    SpecialProjectsCount: int = Field(..., ge=0, le=50)
    TenureDays: Optional[int] = Field(0, ge=0)
    DaysSinceLastReview: Optional[int] = Field(0, ge=0)
    PerfScoreID: Optional[int] = Field(3, ge=1, le=4)
    EmpStatusID: Optional[int] = Field(1, ge=1, le=5)

    @validator("EngagementSurvey")
    def engagement_precision(cls, v):
        return round(v, 2)


def risk_label(score: float) -> str:
    if score >= 0.60:
        return "High"
    elif score >= 0.35:
        return "Medium"
    return "Low"


@app.get("/health")
async def health():
    return {
        "status": app_state["status"],
        "ready": app_state["ready"],
        "error": app_state["error"],
        "version": "1.0.0",
    }


@app.post("/predict")
async def predict(employee: EmployeeInput, api_key: str = Depends(verify_api_key)):
    require_ready()
    try:
        from model.explain import get_local_explanation, recommend_actions

        features = employee.dict()
        explanation = get_local_explanation(features)
        actions = recommend_actions(explanation)
        return {
            **explanation,
            "risk_label": risk_label(explanation["risk_score"]),
            "recommendations": actions,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/employees")
async def get_employees(api_key: str = Depends(verify_api_key)):
    require_ready()
    df = pd.read_csv(DATA_PROCESSED_PATH)

    from model.explain import load_artifacts

    model, scaler, features = load_artifacts()

    feature_cols = [f for f in features if f in df.columns]
    X_scaled = scaler.transform(df[feature_cols].fillna(0))
    proba = model.predict_proba(X_scaled)[:, 1]

    results = []
    for i, row in df.iterrows():
        score = float(proba[i])
        results.append(
            {
                "anon_id": row.get("anon_id", f"emp_{i }"),
                "risk_score": round(score, 4),
                "risk_label": risk_label(score),
                "department": int(row.get("Department", 0)),
                "position": int(row.get("Position", 0)),
                "engagement": float(row.get("EngagementSurvey", 0)),
                "satisfaction": int(row.get("EmpSatisfaction", 0)),
                "absences": int(row.get("Absences", 0)),
                "actually_left": int(row.get("Termd", 0)),
            }
        )
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"employees": results, "total": len(results)}


@app.get("/dashboard/stats")
async def dashboard_stats(api_key: str = Depends(verify_api_key)):
    require_ready()
    df = pd.read_csv(DATA_PROCESSED_PATH)

    from model.explain import load_artifacts, get_global_importance

    model, scaler, features = load_artifacts()
    feature_cols = [f for f in features if f in df.columns]
    X_scaled = scaler.transform(df[feature_cols].fillna(0))
    proba = model.predict_proba(X_scaled)[:, 1]
    df["risk_score"] = proba

    high = int((df["risk_score"] >= 0.60).sum())
    medium = int(((df["risk_score"] >= 0.35) & (df["risk_score"] < 0.60)).sum())
    low = int((df["risk_score"] < 0.35).sum())

    dept_attrition = []
    if "Department" in df.columns:
        for dept, gdf in df.groupby("Department"):
            dept_attrition.append(
                {
                    "department": int(dept),
                    "attrition_rate": round(float(gdf["Termd"].mean()), 3),
                    "avg_risk": round(float(gdf["risk_score"].mean()), 3),
                    "count": len(gdf),
                }
            )

    try:
        feat_importance = get_global_importance(DATA_PROCESSED_PATH)["importance"][:10]
    except Exception:
        feat_importance = []

    metrics_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
    metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)

    return {
        "total_employees": len(df),
        "attrition_rate": round(float(df["Termd"].mean()), 3),
        "avg_engagement": round(float(df["EngagementSurvey"].mean()), 2),
        "avg_satisfaction": round(float(df["EmpSatisfaction"].mean()), 2),
        "avg_absences": round(float(df["Absences"].mean()), 2),
        "high_risk_count": high,
        "medium_risk_count": medium,
        "low_risk_count": low,
        "dept_attrition": dept_attrition,
        "feature_importance": feat_importance,
        "model_metrics": metrics,
    }


@app.get("/explain/{anon_id}")
async def explain_employee(anon_id: str, api_key: str = Depends(verify_api_key)):
    require_ready()
    df = pd.read_csv(DATA_PROCESSED_PATH)
    row = df[df["anon_id"] == anon_id]
    if row.empty:
        raise HTTPException(status_code=404, detail="Employee not found")

    from model.explain import load_artifacts, get_local_explanation, recommend_actions

    _, scaler, features = load_artifacts()
    feature_cols = [f for f in features if f in df.columns]
    employee_features = row[feature_cols].fillna(0).iloc[0].to_dict()

    explanation = get_local_explanation(employee_features)
    explanation["recommendations"] = recommend_actions(explanation)
    return explanation


@app.get("/metrics")
async def get_metrics(api_key: str = Depends(verify_api_key)):
    metrics_path = os.path.join(ARTIFACTS_DIR, "metrics.json")
    if not os.path.exists(metrics_path):
        raise HTTPException(status_code=503, detail="Model not trained yet")
    with open(metrics_path) as f:
        return json.load(f)
