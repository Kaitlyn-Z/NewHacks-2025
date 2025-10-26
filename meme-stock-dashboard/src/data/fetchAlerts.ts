import { StockAlert } from "@/types";

export const fetchAlerts = async (): Promise<StockAlert[]> => {
  const res = await fetch("http://localhost:8000/api/active_alerts");
  if (!res.ok) throw new Error("Failed to fetch alerts");
  const data: StockAlert[] = await res.json();
  return data;
};