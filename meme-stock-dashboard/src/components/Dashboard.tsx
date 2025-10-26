import React, { useState, useEffect } from 'react';
import StockCard from './StockCard';
import { StockAlert } from '@/types';
import { fetchAlerts } from '../api/alerts'; 

const Dashboard: React.FC = () => {
  const [alerts, setAlerts] = useState<StockAlert[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAlerts() {
      try {
        const data = await fetchAlerts();
        setAlerts(data);
      } catch (err) {
        console.error('Error fetching alerts:', err);
      } finally {
        setLoading(false);
      }
    }

    loadAlerts();

    // Optional: poll every 10s
    const interval = setInterval(loadAlerts, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <p>Loading alerts...</p>;

  return (
    <div style={{ padding: '2rem' }}>
      <h1>Stock Dashboard</h1>
      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        {alerts.map(alert => (
          <StockCard key={alert.id} alert={alert} />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
