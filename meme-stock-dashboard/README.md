# 🚀 Meme Stock Alerts Dashboard

A real-time dashboard for monitoring meme stock activity based on social sentiment analysis and volume data.

## Features

- **Real-time Alerts**: Auto-refreshing dashboard with 30-second updates
- **Social Sentiment**: Tracks mention counts from social platforms
- **Volume Analysis**: Monitors trading volume ratios vs historical averages
- **Priority System**: High/Medium/Low priority alerts based on activity levels
- **Interactive Charts**: Volume trend visualization for each stock
- **Email Notifications**: Automated email alerts for high-priority stocks
- **SMTP Integration**: Configurable email settings with multiple providers
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Email**: Nodemailer with SMTP support
- **Data**: Mock data with realistic stock information

## Getting Started

1. **Install Dependencies**
   ```bash
   npm install
   ```

2. **Run Development Server**
   ```bash
   npm run dev
   ```

3. **Configure Email (Optional)**
   ```bash
   cp env.example .env.local
   # Edit .env.local with your email settings
   ```

4. **Open Browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Project Structure

```
src/
├── app/
│   ├── api/
│   │   └── email/
│   │       └── route.ts     # Email notification API
│   ├── globals.css          # Global styles
│   ├── layout.tsx           # Root layout
│   └── page.tsx             # Main dashboard
├── components/
│   ├── AlertBadge.tsx       # Priority badge component
│   ├── EmailSettings.tsx    # Email configuration modal
│   ├── StockCard.tsx        # Individual stock alert card
│   └── VolumeChart.tsx      # Volume visualization chart
├── data/
│   └── mockData.ts          # Mock stock data
├── lib/
│   └── emailService.ts      # Email service with SMTP
└── types/
    ├── email.ts             # Email-related types
    └── index.ts             # Main TypeScript interfaces
```

## Key Components

### Dashboard (`page.tsx`)
- Main application with auto-refresh functionality
- Statistics overview cards
- Alert management and display

### StockCard (`StockCard.tsx`)
- Individual stock alert display
- Price and volume information
- Interactive volume charts
- Priority indicators

### VolumeChart (`VolumeChart.tsx`)
- Recharts-based volume visualization
- Current vs average volume comparison
- Interactive tooltips and legends

### EmailService (`emailService.ts`)
- Nodemailer-based email service
- HTML email templates with responsive design
- SMTP configuration for multiple providers
- Priority-based notification filtering

### EmailSettings (`EmailSettings.tsx`)
- User-friendly email configuration modal
- SMTP settings with test connection
- Priority-based notification preferences
- Settings persistence in localStorage

## Mock Data

The application includes realistic mock data featuring:
- Popular meme stocks (GME, AMC, BB, etc.)
- Realistic mention counts and volume ratios
- Price movements and timestamps
- Priority classifications

## Email Configuration

### Gmail Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: Google Account → Security → App passwords
3. Use the App Password (not your regular password) in SMTP_PASS

### Other Email Providers
- **Outlook**: `smtp-mail.outlook.com`, port 587
- **Yahoo**: `smtp.mail.yahoo.com`, port 587
- **Custom SMTP**: Use your provider's SMTP settings

### Email Features
- **HTML Templates**: Beautiful, responsive email designs
- **Priority Filtering**: Choose which alert levels trigger emails
- **Test Connection**: Verify SMTP settings before saving
- **Real-time Stats**: Track sent/failed email counts

## Future Enhancements

- **Enhanced Sentiment Sources**: Integrate additional data sources for sentiment analysis
- **User Authentication**: Personal watchlists and preferences
- **Push Notifications**: Real-time alerts via browser notifications
- **Historical Analysis**: Long-term trend analysis and backtesting
- **Mobile App**: React Native version for mobile devices
- **Email Templates**: Customizable email designs
- **Webhook Integration**: Slack, Discord, Telegram notifications

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

### Key Features Implemented

✅ **Auto-refresh every 30 seconds**
✅ **Responsive grid layout**
✅ **Priority-based alert system**
✅ **Interactive volume charts**
✅ **Real-time statistics**
✅ **Email notifications with SMTP**
✅ **HTML email templates**
✅ **Email settings configuration**
✅ **Modern UI with Tailwind CSS**
✅ **TypeScript for type safety**
✅ **Component-based architecture**

## Demo

The dashboard automatically refreshes and simulates real-time data updates. You can:
- Toggle auto-refresh on/off
- Manually refresh data
- View detailed volume charts
- See priority-based alert classifications
- Configure email notifications
- Test SMTP connections
- Receive HTML email alerts

Perfect for hackathon demonstrations and rapid prototyping!
