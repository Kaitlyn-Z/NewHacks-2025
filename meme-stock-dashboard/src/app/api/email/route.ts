import { NextRequest, NextResponse } from 'next/server';
import { EmailService } from '@/lib/emailService';
import { EmailSettings, EmailNotification } from '@/types/email';

// Default email settings - in production, these would come from environment variables
const defaultEmailSettings: EmailSettings = {
  enabled: process.env.EMAIL_ENABLED === 'true',
  email: process.env.EMAIL_RECIPIENT || 'your-email@example.com',
  highPriorityOnly: true,
  mediumPriorityOnly: false,
  lowPriorityOnly: false,
  smtpConfig: {
    host: process.env.SMTP_HOST || 'smtp.gmail.com',
    port: parseInt(process.env.SMTP_PORT || '587'),
    secure: process.env.SMTP_SECURE === 'true',
    auth: {
      user: process.env.SMTP_USER || 'your-email@gmail.com',
      pass: process.env.SMTP_PASS || 'your-app-password',
    },
  },
};

let emailService: EmailService | null = null;

function getEmailService(): EmailService {
  if (!emailService) {
    emailService = new EmailService(defaultEmailSettings);
  }
  return emailService;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { action, alert, settings } = body;

    switch (action) {
      case 'send-alert':
        if (!alert) {
          return NextResponse.json({ error: 'Alert data required' }, { status: 400 });
        }

        const service = getEmailService();
        const success = await service.sendAlert(alert as EmailNotification);
        
        return NextResponse.json({ 
          success, 
          message: success ? 'Email sent successfully' : 'Failed to send email' 
        });

      case 'send-bulk-alerts':
        if (!alert || !Array.isArray(alert)) {
          return NextResponse.json({ error: 'Alerts array required' }, { status: 400 });
        }

        const bulkService = getEmailService();
        const result = await bulkService.sendBulkAlerts(alert as EmailNotification[]);
        
        return NextResponse.json({ 
          success: result.failed === 0,
          sent: result.sent,
          failed: result.failed,
          message: `Sent ${result.sent} emails, ${result.failed} failed`
        });

      case 'test-connection':
        const testService = getEmailService();
        const isConnected = await testService.testConnection();
        
        return NextResponse.json({ 
          success: isConnected,
          message: isConnected ? 'Email service connected successfully' : 'Email service connection failed'
        });

      case 'update-settings':
        if (!settings) {
          return NextResponse.json({ error: 'Settings data required' }, { status: 400 });
        }

        // Update email service with new settings
        emailService = new EmailService(settings as EmailSettings);
        
        return NextResponse.json({ 
          success: true,
          message: 'Email settings updated successfully'
        });

      default:
        return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
    }
  } catch (error) {
    console.error('Email API error:', error);
    return NextResponse.json({ 
      error: 'Internal server error',
      message: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

export async function GET() {
  return NextResponse.json({ 
    message: 'Email notification API',
    endpoints: {
      'POST /api/email': 'Send email notifications',
      actions: ['send-alert', 'send-bulk-alerts', 'test-connection', 'update-settings']
    }
  });
}
