import React, { useState } from 'react';

function Settings() {
  const [settings, setSettings] = useState({
    email: 'user@example.com',
    fullName: 'Your Name',
    organization: 'Your Company',
    theme: 'light',
    notifications: true,
    autoDownload: false,
  });

  const [saved, setSaved] = useState(false);

  const handleChange = (key, value) => {
    setSettings((prev) => ({ ...prev, [key]: value }));
    setSaved(false);
  };

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="space-y-6 max-w-2xl">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">Settings</h1>
        <p className="text-slate-600 mt-1">Manage your account and preferences</p>
      </div>

      {/* Success Message */}
      {saved && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-green-700 text-sm font-medium">
          ✓ Settings saved successfully
        </div>
      )}

      {/* Account Settings */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4">Account Settings</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Full Name
            </label>
            <input
              type="text"
              value={settings.fullName}
              onChange={(e) => handleChange('fullName', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Email Address
            </label>
            <input
              type="email"
              value={settings.email}
              onChange={(e) => handleChange('email', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Organization
            </label>
            <input
              type="text"
              value={settings.organization}
              onChange={(e) => handleChange('organization', e.target.value)}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Preferences */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4">Preferences</h2>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-slate-900">
                Theme
              </label>
              <p className="text-xs text-slate-600">
                Choose your preferred interface theme
              </p>
            </div>
            <select
              value={settings.theme}
              onChange={(e) => handleChange('theme', e.target.value)}
              className="px-3 py-2 border border-slate-300 rounded-lg text-sm"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="auto">Auto</option>
            </select>
          </div>

          <div className="border-t border-slate-200 pt-4 flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-slate-900">
                Notifications
              </label>
              <p className="text-xs text-slate-600">
                Receive email notifications for important updates
              </p>
            </div>
            <button
              onClick={() => handleChange('notifications', !settings.notifications)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.notifications ? 'bg-indigo-600' : 'bg-slate-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.notifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div className="border-t border-slate-200 pt-4 flex items-center justify-between">
            <div>
              <label className="text-sm font-medium text-slate-900">
                Auto-Download Results
              </label>
              <p className="text-xs text-slate-600">
                Automatically download prediction results
              </p>
            </div>
            <button
              onClick={() => handleChange('autoDownload', !settings.autoDownload)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                settings.autoDownload ? 'bg-indigo-600' : 'bg-slate-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  settings.autoDownload ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
      </div>

      {/* Security */}
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-lg font-bold text-slate-900 mb-4">Security</h2>
        <div className="space-y-3">
          <button className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 text-left">
            🔑 Change Password
          </button>
          <button className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 text-left">
            📊 View Activity Log
          </button>
          <button className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 text-left">
            🔓 Manage Sessions
          </button>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="bg-red-50 border border-red-200 rounded-xl p-6">
        <h2 className="text-lg font-bold text-red-900 mb-4">Danger Zone</h2>
        <button className="px-4 py-2 bg-red-600 text-white rounded-lg text-sm font-medium hover:bg-red-700">
          🗑️ Delete Account
        </button>
        <p className="text-xs text-red-700 mt-2">
          This action cannot be undone. All data will be permanently deleted.
        </p>
      </div>

      {/* Save Button */}
      <button
        onClick={handleSave}
        className="w-full btn-primary py-2 px-4 rounded-lg text-sm font-medium"
      >
        💾 Save Settings
      </button>
    </div>
  );
}

export default Settings;
