import { useEffect, useState } from "react";
import { fetchExplanation } from "../api";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, ReferenceLine
} from "recharts";

export default function ExplainView({ employee, navigate }) {
  const [explanation, setExplanation] = useState(null);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);

  useEffect(() => {
    fetchExplanation(employee.anon_id)
      .then(setExplanation)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [employee.anon_id]);

  if (loading) return <div className="loading">Computing SHAP explanation...</div>;
  if (error)   return <div className="error">{error}</div>;
  if (!explanation) return null;

  const riskPct      = Math.round(explanation.risk_score * 100);
  const baselinePct  = Math.round(explanation.expected_value * 100);
  const deltaPct     = riskPct - baselinePct;

  
  const riskLevel =
    explanation.risk_score >= 0.60 ? "high"
    : explanation.risk_score >= 0.35 ? "medium"
    : "low";

  const riskLabel = { high: "High Attrition Risk", medium: "Medium Attrition Risk", low: "Low Attrition Risk" };
  const riskClass = { high: "risk-hero-red", medium: "risk-hero-yellow", low: "risk-hero-green" };

  
  const waterfallData = explanation.shap_values
    .slice(0, 10)
    .map(s => ({
      feature: s.feature,
      shap:    parseFloat(s.shap.toFixed(4)),
      value:   s.value,
    }));

  return (
    <div className="page">
      <button className="back-btn" onClick={() => navigate("employees")}>
        ← Back to Employee Table
      </button>

      <h1 className="page-title">
        Explanation — <span className="mono">{employee.anon_id}</span>
      </h1>

      {}
      <div className={`risk-hero ${riskClass[riskLevel]}`}>
        <div className="risk-hero-score">{riskPct}%</div>
        <div className="risk-hero-label">{riskLabel[riskLevel]}</div>
        <div className="risk-hero-sub">
          Model baseline (avg. employee): {baselinePct}% &nbsp;·&nbsp;
          This employee: {deltaPct >= 0 ? "+" : ""}{deltaPct}%
        </div>
      </div>

      {}
      <div className="chart-card shap-card">
        <h2>SHAP Waterfall — Why this prediction?</h2>
        <p className="chart-sub">
          Each bar shows how much a feature&nbsp;
          <strong style={{color:"#ef4444"}}>increases (red)</strong> or&nbsp;
          <strong style={{color:"#22c55e"}}>decreases (green)</strong>&nbsp;
          the attrition risk compared to the average employee.
        </p>
        <ResponsiveContainer width="100%" height={340}>
          <BarChart layout="vertical" data={waterfallData} margin={{ left: 10, right: 50 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" tickFormatter={v => v.toFixed(3)} />
            <YAxis dataKey="feature" type="category" width={160} tick={{ fontSize: 12 }} />
            <Tooltip
              formatter={(val, _, props) => [
                `SHAP: ${Number(val).toFixed(4)} | Value: ${props.payload.value}`,
                props.payload.feature,
              ]}
            />
            <ReferenceLine x={0} stroke="#374151" strokeWidth={2} />
            <Bar dataKey="shap" radius={[0, 4, 4, 0]}>
              {waterfallData.map((entry, i) => (
                <Cell
                  key={i}
                  fill={entry.shap > 0 ? "#ef4444" : "#22c55e"}
                  fillOpacity={0.85}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {}
      <div className="explain-grid">
        <div className="factor-card risk-card">
          <h2>Top Risk Factors</h2>
          {explanation.top_risk_factors.length === 0
            ? <p style={{color:"#64748b",fontSize:"0.85rem"}}>No significant risk factors detected.</p>
            : <ul>{explanation.top_risk_factors.map(f => <li key={f}>{f}</li>)}</ul>
          }
        </div>
        <div className="factor-card protect-card">
          <h2>Protective Factors</h2>
          {explanation.top_protective_factors.length === 0
            ? <p style={{color:"#64748b",fontSize:"0.85rem"}}>No significant protective factors detected.</p>
            : <ul>{explanation.top_protective_factors.map(f => <li key={f}>{f}</li>)}</ul>
          }
        </div>
      </div>

      {}
      {explanation.recommendations?.length > 0 && (
        <div className="reco-section">
          <h2>Recommended HR Actions</h2>
          <div className="reco-grid">
            {explanation.recommendations.map((r, i) => (
              <div key={i} className={`reco-card priority-${r.priority.toLowerCase()}`}>
                <div className="reco-header">
                  <span className="reco-title">{r.title}</span>
                  <span className={`badge priority-badge-${r.priority.toLowerCase()}`}>
                    {r.priority} Priority
                  </span>
                </div>
                <p className="reco-action">{r.action}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {}
      <div className="disclaimer-box">
        <strong>Human-in-the-Loop Notice</strong>
        <p>
          This explanation is generated by an AI model and is intended solely as
          decision support for qualified HR professionals. No automated employment
          decision should be made based on these predictions alone. Always validate
          findings with direct manager input and consider contextual factors not
          captured in this dataset.
        </p>
      </div>
    </div>
  );
}
