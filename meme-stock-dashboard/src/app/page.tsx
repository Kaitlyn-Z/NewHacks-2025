'use client';

import React, { useState, useEffect } from 'react';
import { RefreshCw, Activity, TrendingUp, AlertTriangle, Clock, Mail, Settings } from 'lucide-react';
import { StockAlert } from '@/types';
import { EmailSettings } from '@/types/email';
import { mockStockAlerts, generateRandomAlert } from '@/data/mockData';
import StockCard from '@/components/StockCard';
import SimpleEmailSettingsModal, { AlertPreferences } from '@/components/SimpleEmailSettings';

export default function Dashboard() {
  const [alerts, setAlerts] = useState<StockAlert[]>(mockStockAlerts);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [mounted, setMounted] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [userEmail, setUserEmail] = useState<string>('');
  const [emailEnabled, setEmailEnabled] = useState(false);
  const [showEmailSettings, setShowEmailSettings] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState<{ sent: number; failed: number }>({ sent: 0, failed: 0 });
  const [alertPreferences, setAlertPreferences] = useState<AlertPreferences>({
    high: true,
    medium: true,
    low: false
  });

  const sendEmailNotification = async (alert: StockAlert) => {
    if (!emailEnabled || !userEmail) return;

    try {
      const response = await fetch('http://localhost:5002/api/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'send-alert',
          alert: {
            ...alert,
            emailSent: false,
          },
          email: userEmail,
        }),
      });

      const result = await response.json();
      if (result.success) {
        setEmailNotifications(prev => ({ ...prev, sent: prev.sent + 1 }));
      } else {
        setEmailNotifications(prev => ({ ...prev, failed: prev.failed + 1 }));
      }
    } catch (error) {
      console.error('Failed to send email notification:', error);
      setEmailNotifications(prev => ({ ...prev, failed: prev.failed + 1 }));
    }
  };

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      // Fetch real data from integrated backend
      const response = await fetch('http://localhost:5001/api/alerts?refresh=true');
      const data = await response.json();
      
      if (data.success && data.alerts) {
        const previousAlerts = alerts;
        setAlerts(data.alerts);
        
        // Check for new alerts matching user preferences and send email notifications
        if (emailEnabled && userEmail) {
          const shouldSendAlert = (priority: string) => {
            if (priority === 'high') return alertPreferences.high;
            if (priority === 'medium') return alertPreferences.medium;
            if (priority === 'low') return alertPreferences.low;
            return false;
          };
          
          const newAlerts = data.alerts.filter((alert: StockAlert) => 
            shouldSendAlert(alert.priority) &&
            !previousAlerts.some(prev => prev.ticker === alert.ticker && prev.priority === alert.priority)
          );
          
          for (const alert of newAlerts) {
            await sendEmailNotification(alert);
          }
        }
      } else {
        console.error('Failed to fetch alerts:', data.error);
      }
      
      setLastUpdated(new Date());
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
      // Fallback to mock data on error
      if (alerts.length === 0) {
        setAlerts(mockStockAlerts);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Mark component as mounted to prevent hydration errors
    setMounted(true);
    
    // Load user email from localStorage
    const savedEmail = localStorage.getItem('userEmail');
    const savedEnabled = localStorage.getItem('emailEnabled') === 'true';
    if (savedEmail) {
      setUserEmail(savedEmail);
      setEmailEnabled(savedEnabled);
    }
    
    // Load alert preferences from localStorage
    const savedPreferences = localStorage.getItem('alertPreferences');
    if (savedPreferences) {
      setAlertPreferences(JSON.parse(savedPreferences));
    }
    
    // Fetch initial data
    fetchAlerts();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(fetchAlerts, 1800000); // 30 minutes (matches scheduler)
      return () => clearInterval(interval);
    }
  }, [autoRefresh, emailEnabled, userEmail]);

  const handleManualRefresh = () => {
    fetchAlerts();
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  const handleEmailSave = (email: string, preferences: AlertPreferences) => {
    setUserEmail(email);
    setEmailEnabled(true);
    setAlertPreferences(preferences);
    localStorage.setItem('userEmail', email);
    localStorage.setItem('emailEnabled', 'true');
    localStorage.setItem('alertPreferences', JSON.stringify(preferences));
  };

  const getStats = () => {
    const highAlerts = alerts.filter(alert => alert.priority === 'high').length;
    const mediumAlerts = alerts.filter(alert => alert.priority === 'medium').length;
    const lowAlerts = alerts.filter(alert => alert.priority === 'low').length;
    const totalMentions = alerts.reduce((sum, alert) => sum + alert.mentionCount, 0);
    
    return { highAlerts, mediumAlerts, lowAlerts, totalMentions };
  };

  const stats = getStats();

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Meme Stock Alerts</h1>
                <p className="text-sm text-gray-600">Real-time social sentiment analysis</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-gray-600">
                <Clock className="w-4 h-4" />
                <span>Last updated: {mounted ? lastUpdated.toLocaleTimeString() : '--:--:--'}</span>
              </div>
              
              <button
                onClick={toggleAutoRefresh}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  autoRefresh 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-600'
                }`}
              >
                Auto-refresh {autoRefresh ? 'ON' : 'OFF'}
              </button>
              
              <button
                onClick={() => setShowEmailSettings(true)}
                className="flex items-center space-x-2 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
              >
                <Settings className="w-4 h-4" />
                <span>Email Settings</span>
              </button>
              
              <button
                onClick={handleManualRefresh}
                disabled={loading}
                className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
                <span>Refresh</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Cards */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-red-500">
            <div className="flex items-center">
              <AlertTriangle className="w-8 h-8 text-red-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">High Priority</p>
                <p className="text-2xl font-bold text-gray-900">{stats.highAlerts}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-yellow-500">
            <div className="flex items-center">
              <Activity className="w-8 h-8 text-yellow-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Medium Priority</p>
                <p className="text-2xl font-bold text-gray-900">{stats.mediumAlerts}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-green-500">
            <div className="flex items-center">
              <TrendingUp className="w-8 h-8 text-green-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Low Priority</p>
                <p className="text-2xl font-bold text-gray-900">{stats.lowAlerts}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6 border-l-4 border-blue-500">
            <div className="flex items-center">
              <Activity className="w-8 h-8 text-blue-500" />
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Mentions</p>
                <p className="text-2xl font-bold text-gray-900">{stats.totalMentions.toLocaleString()}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Alerts Grid */}
        <div className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Active Alerts</h2>
            <div className="text-sm text-gray-600">
              {alerts.length} alert{alerts.length !== 1 ? 's' : ''} detected
            </div>
          </div>
          
          {loading && (
            <div className="flex justify-center py-8">
              <div className="flex items-center space-x-2 text-gray-600">
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Updating alerts...</span>
              </div>
            </div>
          )}
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {alerts.map((alert) => (
              <StockCard key={alert.id} alert={alert} />
            ))}
          </div>
          
          {alerts.length === 0 && !loading && (
            <div className="text-center py-12">
              <Activity className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No alerts detected</h3>
              <p className="text-gray-600">Monitoring social platforms for meme stock activity...</p>
            </div>
          )}
        </div>
      </div>

      {/* Email Settings Modal */}
      <SimpleEmailSettingsModal
        isOpen={showEmailSettings}
        onClose={() => setShowEmailSettings(false)}
        onSave={handleEmailSave}
      />
    </div>
  );
}
