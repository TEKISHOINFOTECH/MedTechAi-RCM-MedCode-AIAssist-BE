import { Settings as SettingsIcon, Brain, Shield, Bell, Database } from 'lucide-react';
import { Logo } from '../components/Logo';

export function Settings() {
  return (
    <main className="py-8">
      <div className="mb-8">
        <div className="flex items-center space-x-4 mb-4">
          <Logo size="lg" />
          <div>
            <h1 className="text-4xl font-bold text-slate-800">Settings</h1>
            <p className="text-slate-700 text-lg font-medium">Configure your AI-powered denial risk analyzer</p>
          </div>
        </div>


      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* AI Model Settings */}
        <div className="enterprise-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Brain className="w-6 h-6 text-purple-600" />
            <h3 className="text-lg font-bold text-slate-900">AI Model Configuration</h3>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Risk Threshold Sensitivity
              </label>
              <select className="select-field">
                <option>Conservative (High Sensitivity)</option>
                <option>Balanced (Default)</option>
                <option>Aggressive (Low Sensitivity)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Code Validation Strictness
              </label>
              <select className="select-field">
                <option>Strict (Flag all potential issues)</option>
                <option>Standard (Flag likely issues)</option>
                <option>Lenient (Flag only critical issues)</option>
              </select>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">Auto-update AI Models</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>
          </div>
        </div>

        {/* Security Settings */}
        <div className="enterprise-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Shield className="w-6 h-6 text-green-600" />
            <h3 className="text-lg font-bold text-slate-900">Security & Privacy</h3>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">Data Encryption</span>
              <span className="status-success">ENABLED</span>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">HIPAA Compliance Mode</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">Audit Logging</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Data Retention Period
              </label>
              <select className="select-field">
                <option>30 days</option>
                <option>90 days</option>
                <option>1 year</option>
                <option>7 years (HIPAA compliant)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Notification Settings */}
        <div className="enterprise-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Bell className="w-6 h-6 text-blue-600" />
            <h3 className="text-lg font-bold text-slate-900">Notifications</h3>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">High Risk Alerts</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">Processing Complete</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" defaultChecked />
                <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-slate-700">Weekly Reports</span>
              <label className="relative inline-flex items-center cursor-pointer">
                <input type="checkbox" className="sr-only peer" />
                <div className="w-11 h-6 bg-slate-600 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
              </label>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-2">
                Email Notifications
              </label>
              <input
                type="email"
                placeholder="admin@healthcare.com"
                className="input-field"
              />
            </div>
          </div>
        </div>

        {/* Integration Settings */}
        <div className="enterprise-card p-6">
          <div className="flex items-center space-x-3 mb-6">
            <Database className="w-6 h-6 text-amber-600" />
            <h3 className="text-lg font-bold text-slate-900">Integrations</h3>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between p-3 border border-slate-200 rounded-lg">
              <div>
                <p className="text-sm font-medium text-slate-900">Epic EMR</p>
                <p className="text-xs text-slate-600">Electronic Medical Records</p>
              </div>
              <span className="status-success">CONNECTED</span>
            </div>

            <div className="flex items-center justify-between p-3 border border-slate-200 rounded-lg">
              <div>
                <p className="text-sm font-medium text-slate-900">Cerner PowerChart</p>
                <p className="text-xs text-slate-600">Clinical Information System</p>
              </div>
              <button className="primary-button text-sm px-3 py-1">
                CONNECT
              </button>
            </div>

            <div className="flex items-center justify-between p-3 border border-slate-200 rounded-lg">
              <div>
                <p className="text-sm font-medium text-slate-900">Change Healthcare</p>
                <p className="text-xs text-slate-600">Claims Processing</p>
              </div>
              <span className="status-success">CONNECTED</span>
            </div>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="mt-8 flex justify-end">
        <button className="primary-button px-6 py-3">
          Save Settings
        </button>
      </div>
    </main>
  );
}