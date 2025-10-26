import React, { useEffect, useState } from "react";
import StockCard from "./StockCard"; // adjust path if needed
import { StockAlert } from "../types"; // or define the interface locally

const Dashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<StockAlert[]>([]);

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await fetch("http://localhost:8000/alerts"); // your backend endpoint
        const data = await response.json();
        setAlerts(data);
      } catch (err) {
        console.error("Failed to fetch alerts:", err);
      }
    };

    fetchAlerts();
    const interval = setInterval(fetchAlerts, 60000); // refresh every 60s
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="dashboard-container">
      {alerts.length === 0 ? (
        <p>No alerts yet.</p>
      ) : (
        alerts.map((alert) => (
          <StockCard key={alert.id} alert={alert} />
        ))
      )}
    </div>
  );
};

export default Dashboard;
