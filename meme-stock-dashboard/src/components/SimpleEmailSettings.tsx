import React, { useState, useEffect } from 'react';
import { Mail, Settings, TestTube, Save, AlertCircle, CheckCircle } from 'lucide-react';

export interface AlertPreferences {
  high: boolean;
  medium: boolean;
  low: boolean;
}

interface SimpleEmailSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (email: string, preferences: AlertPreferences) => void;
}

const SimpleEmailSettingsModal: React.FC<SimpleEmailSettingsProps> = ({ isOpen, onClose, onSave }) => {
  const [email, setEmail] = useState('');
  const [alertPreferences, setAlertPreferences] = useState<AlertPreferences>({
    high: true,
    medium: true,
    low: false
  });
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    // Load saved email from localStorage
    const savedEmail = localStorage.getItem('userEmail');
    if (savedEmail) {
      setEmail(savedEmail);
    }
    
    // Load saved alert preferences
    const savedPreferences = localStorage.getItem('alertPreferences');
    if (savedPreferences) {
      setAlertPreferences(JSON.parse(savedPreferences));
    }
  }, []);

  const handleSave = async () => {
    setTesting(true);
    setTestResult(null);

    try {
      // First, save the preferences to the FastAPI backend (database)
      await fetch('http://localhost:8000/update-preferences', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: email,
          preferences: alertPreferences,
        }),
      });

      // Also save to the email service backend (in-memory)
      await fetch('http://localhost:5002/api/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'update-preferences',
          email: email,
          preferences: alertPreferences,
        }),
      });

      // Then send a test email
      const response = await fetch('http://localhost:5002/api/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'send-alert',
          email: email,
          alert: {
            ticker: 'TEST',
            priority: 'high',
            mentionCount: 100,
            volumeRatio: 3.5,
            currentPrice: 123.45,
            priceChange: 15.2,
            detectedAt: new Date().toISOString(),
          },
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        setTestResult({
          success: true,
          message: `✅ Test email sent to ${email}! Check your inbox.`,
        });
        
        // Save settings after successful test
        localStorage.setItem('userEmail', email);
        localStorage.setItem('alertPreferences', JSON.stringify(alertPreferences));
        onSave(email, alertPreferences);
        
        // Close modal after 2 seconds
        setTimeout(() => {
          onClose();
        }, 2000);
      } else {
        setTestResult({
          success: false,
          message: 'Failed to send test email: ' + result.message,
        });
      }
    } catch (error) {
      console.error('Email test error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setTestResult({
        success: false,
        message: `Failed to send test email: ${errorMessage}. Make sure the email service is running on port 5002.`,
      });
    } finally {
      setTesting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <Mail className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-900">Email Notifications</h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <div className="space-y-6">
            {/* Email Address Input */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Your Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="your-email@example.com"
              />
              <p className="text-sm text-gray-600 mt-1">
                We'll send meme stock alerts to this email address
              </p>
            </div>

            {/* Alert Priority Preferences */}
            <div className="bg-gradient-to-br from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200">
              <h4 className="font-medium text-gray-900 mb-3">📬 Alert Preferences</h4>
              <p className="text-sm text-gray-600 mb-3">
                Choose which priority levels you want to receive via email:
              </p>
              <div className="space-y-3">
                <label className="flex items-center p-3 bg-white rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="checkbox"
                    checked={alertPreferences.high}
                    onChange={(e) => setAlertPreferences({ ...alertPreferences, high: e.target.checked })}
                    className="w-4 h-4 text-red-600 bg-gray-100 border-gray-300 rounded focus:ring-red-500"
                  />
                  <div className="ml-3 flex-1">
                    <span className="text-sm font-medium text-gray-900">🔥 High Priority</span>
                    <p className="text-xs text-gray-500">Critical alerts with exceptional volume spikes</p>
                  </div>
                </label>
                
                <label className="flex items-center p-3 bg-white rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="checkbox"
                    checked={alertPreferences.medium}
                    onChange={(e) => setAlertPreferences({ ...alertPreferences, medium: e.target.checked })}
                    className="w-4 h-4 text-yellow-600 bg-gray-100 border-gray-300 rounded focus:ring-yellow-500"
                  />
                  <div className="ml-3 flex-1">
                    <span className="text-sm font-medium text-gray-900">⚡ Medium Priority</span>
                    <p className="text-xs text-gray-500">Significant alerts with notable activity</p>
                  </div>
                </label>
                
                <label className="flex items-center p-3 bg-white rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                  <input
                    type="checkbox"
                    checked={alertPreferences.low}
                    onChange={(e) => setAlertPreferences({ ...alertPreferences, low: e.target.checked })}
                    className="w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500"
                  />
                  <div className="ml-3 flex-1">
                    <span className="text-sm font-medium text-gray-900">📈 Low Priority</span>
                    <p className="text-xs text-gray-500">Minor alerts with moderate activity</p>
                  </div>
                </label>
              </div>
              {!alertPreferences.high && !alertPreferences.medium && !alertPreferences.low && (
                <div className="mt-3 p-2 bg-yellow-100 rounded-lg">
                  <p className="text-xs text-yellow-800">⚠️ Select at least one priority level to receive alerts</p>
                </div>
              )}
            </div>

            {/* Pre-configured Info */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h4 className="font-medium text-blue-900">Pre-configured Email Service</h4>
                  <p className="text-sm text-blue-700 mt-1">
                    Email notifications are sent from our secure Gmail service. 
                    No additional configuration needed!
                  </p>
                </div>
              </div>
            </div>

            {/* Status Message */}
            {testResult && (
              <div className={`p-4 rounded-lg flex items-center space-x-2 ${
                testResult.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {testResult.success ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <AlertCircle className="w-5 h-5" />
                )}
                <span className="text-sm font-medium">{testResult.message}</span>
              </div>
            )}

            {/* Features List */}
            <div className="bg-green-50 p-4 rounded-lg">
              <h4 className="font-medium text-green-900 mb-2">What You'll Receive:</h4>
              <ul className="text-sm text-green-800 space-y-1">
                <li>✓ Real-time alerts for your selected priority levels</li>
                <li>✓ Beautiful HTML email templates</li>
                <li>✓ Stock data and volume analysis</li>
                <li>✓ AI-powered investment insights</li>
                <li>✓ Direct links to the dashboard</li>
              </ul>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!email || testing || (!alertPreferences.high && !alertPreferences.medium && !alertPreferences.low)}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Mail className="w-4 h-4" />
              <span>{testing ? 'Sending Test Email...' : 'Save & Send Test Email'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleEmailSettingsModal;
