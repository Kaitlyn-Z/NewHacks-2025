import { StockAlert } from '@/types';

export async function fetchAlerts(): Promise<StockAlert[]> {
  try {
    const response = await fetch('http://localhost:5001/api/alerts?refresh=true');
    const data = await response.json();

    if (data.success && Array.isArray(data.alerts)) {
      return data.alerts;
    } else {
      console.error('Invalid alerts response:', data);
      return [];
    }
  } catch (err) {
    console.error('Error fetching alerts:', err);
    return [];
  }
}

