export interface EmailNotification {
  id: string;
  ticker: string;
  priority: 'high' | 'medium' | 'low';
  mentionCount: number;
  volumeRatio: number;
  currentPrice: number;
  priceChange: number;
  detectedAt: string;
  sentAt?: string;
  emailSent: boolean;
}

export interface EmailSettings {
  enabled: boolean;
  email: string;
  highPriorityOnly: boolean;
  mediumPriorityOnly: boolean;
  lowPriorityOnly: boolean;
  smtpConfig: {
    host: string;
    port: number;
    secure: boolean;
    auth: {
      user: string;
      pass: string;
    };
  };
}

export interface EmailTemplate {
  subject: string;
  html: string;
  text: string;
}
