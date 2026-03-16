import { useEffect, useState } from "react";
import { fetchEmployees } from "../api";

const RISK_COLORS = { High: "#fef2f2", Medium: "#fffbeb", Low: "#f0fdf4" };
const RISK_BADGE = { High: "badge-red", Medium: "badge-yellow", Low: "badge-green" };

export default function EmployeeTable({ navigate }) {
  const [employees, setEmployees] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("All");
  const [search, setSearch] = useState("");

  useEffect(() => {
    fetchEmployees()
      .then((data) => {
        setEmployees(data.employees);
        setFiltered(data.employees);
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    let list = employees;
    if (filter !== "All") list = list.filter((e) => e.risk_label === filter);
    if (search) list = list.filter((e) => e.anon_id.toLowerCase().includes(search.toLowerCase()));
    setFiltered(list);
  }, [filter, search, employees]);

  if (loading) return <div className="loading">Loading employees...</div>;

  return (
    <div className="page">
      <h1 className="page-title">Employee Risk Assessment</h1>

      <div className="table-controls">
        <input
          className="search-input"
          placeholder="Search by anonymized ID..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <div className="filter-buttons">
          {["All", "High", "Medium", "Low"].map((r) => (
            <button
              key={r}
              className={`filter-btn ${filter === r ? "active" : ""}`}
              onClick={() => setFilter(r)}
            >
              {r} {r !== "All" && `(${employees.filter((e) => e.risk_label === r).length})`}
            </button>
          ))}
        </div>
      </div>

      <p className="disclaimer">
        All employee names have been anonymized in compliance with GDPR.
        Predictions are for decision support only.
      </p>

      <div className="table-wrapper">
        <table className="emp-table">
          <thead>
            <tr>
              <th>Anon ID</th>
              <th>Risk Score</th>
              <th>Risk Level</th>
              <th>Engagement</th>
              <th>Satisfaction</th>
              <th>Absences</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((emp) => (
              <tr
                key={emp.anon_id}
                style={{ backgroundColor: RISK_COLORS[emp.risk_label] }}
              >
                <td className="mono">{emp.anon_id}</td>
                <td>
                  <RiskBar score={emp.risk_score} />
                </td>
                <td>
                  <span className={`badge ${RISK_BADGE[emp.risk_label]}`}>
                    {emp.risk_label}
                  </span>
                </td>
                <td>{emp.engagement?.toFixed(1)}/5</td>
                <td>{emp.satisfaction}/5</td>
                <td>{emp.absences}</td>
                <td>
                  <button
                    className="btn-explain"
                    onClick={() => navigate("explain", emp)}
                  >
                    Explain →
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function RiskBar({ score }) {
  const pct = Math.round(score * 100);
  const color = score >= 0.65 ? "#ef4444" : score >= 0.35 ? "#f59e0b" : "#22c55e";
  return (
    <div className="risk-bar-wrapper">
      <div className="risk-bar-bg">
        <div className="risk-bar-fill" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="risk-pct">{pct}%</span>
    </div>
  );
}
