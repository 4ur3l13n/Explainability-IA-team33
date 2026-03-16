import { useState } from "react";
import Dashboard from "./pages/Dashboard";
import EmployeeTable from "./pages/EmployeeTable";
import ExplainView from "./pages/ExplainView";
import Navbar from "./components/Navbar";
import "./index.css";

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [selectedEmployee, setSelectedEmployee] = useState(null);

  const navigate = (p, employee = null) => {
    setPage(p);
    if (employee) setSelectedEmployee(employee);
  };

  return (
    <div className="app">
      <Navbar page={page} navigate={navigate} />
      <main className="main-content">
        {page === "dashboard" && <Dashboard navigate={navigate} />}
        {page === "employees" && (
          <EmployeeTable navigate={navigate} />
        )}
        {page === "explain" && selectedEmployee && (
          <ExplainView employee={selectedEmployee} navigate={navigate} />
        )}
      </main>
      <footer className="footer">
        <p>
          <strong>Human-in-the-loop disclaimer:</strong> AttritionIQ predictions are
          decision-support tools only. All HR decisions must be validated by a
          qualified HR professional. This system does not make autonomous employment decisions.
        </p>
      </footer>
    </div>
  );
}
