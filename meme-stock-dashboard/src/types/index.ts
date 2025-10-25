export interface StockAlert {
  id: string;
  ticker: string;
  mentionCount: number;
  volumeRatio: number;
  currentPrice: number;
  priceChange: number;
  detectedAt: string;
  priority: 'high' | 'medium' | 'low';
  advice?: string;
}

export interface VolumeData {
  time: string;
  volume: number;
  average: number;
}

export interface AlertBadgeProps {
  priority: 'high' | 'medium' | 'low';
}

export interface StockCardProps {
  alert: StockAlert;
}

export interface VolumeChartProps {
  data: VolumeData[];
  ticker: string;
}
