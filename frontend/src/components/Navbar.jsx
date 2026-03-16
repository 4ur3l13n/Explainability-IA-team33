export default function Navbar({ page, navigate }) {
  return (
    <nav className="navbar">
      <div className="navbar-brand" onClick={() => navigate("dashboard")}>
        <span className="brand-icon"></span>
        <span className="brand-name">AttritionIQ</span>
        <span className="brand-tag">Explainable AI · HR</span>
      </div>
      <div className="navbar-links">
        <button
          className={`nav-link ${page === "dashboard" ? "active" : ""}`}
          onClick={() => navigate("dashboard")}
        >
          Dashboard
        </button>
        <button
          className={`nav-link ${page === "employees" ? "active" : ""}`}
          onClick={() => navigate("employees")}
        >
          Employees
        </button>
      </div>
    </nav>
  );
}
