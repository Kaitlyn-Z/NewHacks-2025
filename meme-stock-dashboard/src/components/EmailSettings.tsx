import React, { useState, useEffect } from 'react';
import { Mail, Settings, TestTube, Save, AlertCircle } from 'lucide-react';
import { EmailSettings } from '@/types/email';

interface EmailSettingsProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (settings: EmailSettings) => void;
}

const EmailSettingsModal: React.FC<EmailSettingsProps> = ({ isOpen, onClose, onSave }) => {
  const [settings, setSettings] = useState<EmailSettings>({
    enabled: false,
    email: '',
    highPriorityOnly: true,
    mediumPriorityOnly: false,
    lowPriorityOnly: false,
    smtpConfig: {
      host: 'smtp.gmail.com',
      port: 587,
      secure: false,
      auth: {
        user: '',
        pass: '',
      },
    },
  });

  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);

  useEffect(() => {
    // Load saved settings from localStorage
    const savedSettings = localStorage.getItem('emailSettings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem('emailSettings', JSON.stringify(settings));
    onSave(settings);
    onClose();
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);

    try {
      // First update settings
      await fetch('http://localhost:5001/api/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'update-settings',
          settings: settings,
        }),
      });

      // Then test connection
      const response = await fetch('http://localhost:5001/api/email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'test-connection',
        }),
      });

      const result = await response.json();
      setTestResult(result);
    } catch (error) {
      setTestResult({
        success: false,
        message: 'Failed to test connection: ' + (error as Error).message,
      });
    } finally {
      setTesting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <Mail className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-900">Email Notification Settings</h2>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          </div>

          <div className="space-y-6">
            {/* Enable/Disable */}
            <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div>
                <h3 className="font-medium text-gray-900">Email Notifications</h3>
                <p className="text-sm text-gray-600">Enable or disable email alerts</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={settings.enabled}
                  onChange={(e) => setSettings({ ...settings, enabled: e.target.checked })}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            {/* Email Address */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={settings.email}
                onChange={(e) => setSettings({ ...settings, email: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="your-email@example.com"
              />
            </div>

            {/* Priority Settings */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">Notification Priority</h3>
              <div className="space-y-3">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.highPriorityOnly}
                    onChange={(e) => setSettings({ ...settings, highPriorityOnly: e.target.checked })}
                    className="mr-3"
                  />
                  <span className="text-sm text-gray-700">High Priority Alerts 🔥</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.mediumPriorityOnly}
                    onChange={(e) => setSettings({ ...settings, mediumPriorityOnly: e.target.checked })}
                    className="mr-3"
                  />
                  <span className="text-sm text-gray-700">Medium Priority Alerts ⚡</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.lowPriorityOnly}
                    onChange={(e) => setSettings({ ...settings, lowPriorityOnly: e.target.checked })}
                    className="mr-3"
                  />
                  <span className="text-sm text-gray-700">Low Priority Alerts 📈</span>
                </label>
              </div>
            </div>

            {/* SMTP Settings */}
            <div>
              <h3 className="font-medium text-gray-900 mb-3">SMTP Configuration</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    SMTP Host
                  </label>
                  <input
                    type="text"
                    value={settings.smtpConfig.host}
                    onChange={(e) => setSettings({
                      ...settings,
                      smtpConfig: { ...settings.smtpConfig, host: e.target.value }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="smtp.gmail.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Port
                  </label>
                  <input
                    type="number"
                    value={settings.smtpConfig.port}
                    onChange={(e) => setSettings({
                      ...settings,
                      smtpConfig: { ...settings.smtpConfig, port: parseInt(e.target.value) }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mt-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value={settings.smtpConfig.auth.user}
                    onChange={(e) => setSettings({
                      ...settings,
                      smtpConfig: { ...settings.smtpConfig, auth: { ...settings.smtpConfig.auth, user: e.target.value } }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="your-email@gmail.com"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password/App Password
                  </label>
                  <input
                    type="password"
                    value={settings.smtpConfig.auth.pass}
                    onChange={(e) => setSettings({
                      ...settings,
                      smtpConfig: { ...settings.smtpConfig, auth: { ...settings.smtpConfig.auth, pass: e.target.value } }
                    })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="your-app-password"
                  />
                </div>
              </div>
            </div>

            {/* Test Connection */}
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="font-medium text-blue-900">Test Email Connection</h4>
                  <p className="text-sm text-blue-700">Verify your SMTP settings work correctly</p>
                </div>
                <button
                  onClick={handleTestConnection}
                  disabled={testing}
                  className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  <TestTube className="w-4 h-4" />
                  <span>{testing ? 'Testing...' : 'Test Connection'}</span>
                </button>
              </div>
              
              {testResult && (
                <div className={`mt-3 p-3 rounded-lg flex items-center space-x-2 ${
                  testResult.success ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  <AlertCircle className="w-4 h-4" />
                  <span className="text-sm">{testResult.message}</span>
                </div>
              )}
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
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Save className="w-4 h-4" />
              <span>Save Settings</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailSettingsModal;
