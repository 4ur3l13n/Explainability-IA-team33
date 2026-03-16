import { useEffect, useState, useCallback } from "react";
import { fetchDashboardStats } from "../api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend
} from "recharts";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function Dashboard({ navigate }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState("starting");
  const [error, setError] = useState(null);

  
  const pollHealth = useCallback(async () => {
    try {
      const res = await fetch(`${BASE_URL}/health`);
      const data = await res.json();
      setBackendStatus(data.status);
      if (data.ready) return true;
      if (data.status === "error") {
        setError(`Backend error: ${data.error}`);
        return true; 
      }
    } catch {
      setBackendStatus("connecting");
    }
    return false;
  }, []);

  useEffect(() => {
    let interval;
    const start = async () => {
      const ready = await pollHealth();
      if (!ready) {
        interval = setInterval(async () => {
          const done = await pollHealth();
          if (done) {
            clearInterval(interval);
            loadStats();
          }
        }, 3000);
      } else {
        loadStats();
      }
    };

    const loadStats = () => {
      fetchDashboardStats()
        .then(setStats)
        .catch(e => setError(e.message))
        .finally(() => setLoading(false));
    };

    start();
    return () => clearInterval(interval);
  }, [pollHealth]);

  if (error) return <div className="error"> {error}</div>;

  if (backendStatus !== "ready" || loading) {
    return (
      <div className="waiting-screen">
        <div className="waiting-card">
          <div className="spinner" />
          <h2>Setting up AttritionIQ...</h2>
          <div className={`status-badge status-${backendStatus}`}>
            {STATUS_LABELS[backendStatus] || backendStatus}
          </div>
          <p className="waiting-sub">
            The model is being trained on first launch (~60s).<br />
            This page will refresh automatically when ready.
          </p>
          <div className="progress-steps">
            <Step label="Start API" done={backendStatus !== "connecting"} />
            <Step label="GDPR Preprocessing" done={["training","ready"].includes(backendStatus)} />
            <Step label="Train XGBoost + Calibration" done={backendStatus === "ready"} />
            <Step label="Ready" done={backendStatus === "ready"} />
          </div>
        </div>
      </div>
    );
  }

  const riskPieData = [
    { name: "High Risk",   value: stats.high_risk_count,   color: "#ef4444" },
    { name: "Medium Risk", value: stats.medium_risk_count, color: "#f59e0b" },
    { name: "Low Risk",    value: stats.low_risk_count,    color: "#22c55e" },
  ];

  return (
    <div className="page">
      <h1 className="page-title">HR Attrition Dashboard</h1>

      <div className="kpi-grid">
        <KpiCard label="Total Employees"     value={stats.total_employees}                       />
        <KpiCard label="Attrition Rate"      value={`${(stats.attrition_rate*100).toFixed(1)}%`} highlight />
        <KpiCard label="Avg Engagement"      value={`${stats.avg_engagement}/5`}                 />
        <KpiCard label="Avg Satisfaction"    value={`${stats.avg_satisfaction}/5`}               />
        <KpiCard label="High Risk Employees" value={stats.high_risk_count}                       highlight />
        {stats.model_metrics?.auc_roc &&
          <KpiCard label="Model AUC-ROC" value={stats.model_metrics.auc_roc} />}
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h2>Risk Distribution</h2>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie data={riskPieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                {riskPieData.map((e,i) => <Cell key={i} fill={e.color} />)}
              </Pie>
              <Legend /><Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>Top Risk Drivers (Global SHAP)</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart layout="vertical" data={stats.feature_importance?.slice(0,8)} margin={{left:20,right:20}}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="feature" type="category" width={130} tick={{fontSize:12}} />
              <Tooltip formatter={v=>v.toFixed(4)} />
              <Bar dataKey="mean_abs_shap" fill="#6366f1" radius={[0,4,4,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2>Attrition Rate by Department</h2>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={stats.dept_attrition}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="department" />
              <YAxis tickFormatter={v=>`${(v*100).toFixed(0)}%`} />
              <Tooltip formatter={v=>`${(v*100).toFixed(1)}%`} />
              <Bar dataKey="attrition_rate" radius={[4,4,0,0]}>
                {stats.dept_attrition.map((e,i) =>
                  <Cell key={i} fill={e.attrition_rate>0.3?"#ef4444":"#6366f1"} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {stats.model_metrics && (
          <div className="chart-card metrics-card">
            <h2>Model Performance</h2>
            <div className="metrics-grid">
              <MetricBadge label="AUC-ROC" value={stats.model_metrics.auc_roc} color="#6366f1" />
              <MetricBadge label="F1 Score" value={stats.model_metrics.f1}     color="#22c55e" />
              <MetricBadge label="Accuracy" value={stats.model_metrics.accuracy} color="#f59e0b" />
            </div>
            <p className="metric-note">5-fold cross-validation · XGBoost + Platt Calibration · SHAP</p>
          </div>
        )}
      </div>

      <button className="btn-primary" onClick={()=>navigate("employees")}> 
        View Employee Risk Table →
      </button>
    </div>
  );
}

const STATUS_LABELS = {
  connecting:      "Connecting to backend...",
  starting:        "Starting up...",
  preprocessing:   "GDPR Preprocessing data...",
  training:        "Training ML model (~60s)...",
  ready:           "Ready",
  error:           "Error",
};

function Step({ label, done }) {
  return (
    <div className={`progress-step ${done ? "done" : ""}`}>
      <span className="step-dot">{done ? "Done" : "In progress"}</span>
      <span>{label}</span>
    </div>
  );
}

function KpiCard({ label, value, icon, highlight }) {
  return (
    <div className={`kpi-card ${highlight?"kpi-highlight":""}`}>
      <span className="kpi-icon">{icon}</span>
      <span className="kpi-value">{value}</span>
      <span className="kpi-label">{label}</span>
    </div>
  );
}

function MetricBadge({ label, value, color }) {
  return (
    <div className="metric-badge" style={{borderColor:color}}>
      <span style={{color}}>{value}</span>
      <small>{label}</small>
    </div>
  );
}
