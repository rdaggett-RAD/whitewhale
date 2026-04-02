import { useState, useEffect } from 'react';
import api from '../api/client';

const STATUS_COLORS = {
  connected: 'bg-emerald-500',
  not_configured: 'bg-yellow-500',
  error: 'bg-red-500',
};

const STATUS_LABELS = {
  connected: 'Connected',
  not_configured: 'Not Configured',
  error: 'Error',
};

export default function Admin() {
  const [tab, setTab] = useState('integrations');
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchIntegrations = async () => {
    setLoading(true);
    try {
      const res = await api.get('/admin/integrations');
      setIntegrations(res.data.integrations);
    } catch {
      setIntegrations([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    if (tab === 'integrations') fetchIntegrations();
  }, [tab]);

  return (
    <div>
      <h2 className="text-xl font-bold text-gray-100 mb-6">Admin</h2>

      <div className="flex gap-4 mb-6 border-b border-gray-800">
        {['integrations', 'tenants'].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`pb-2 text-sm capitalize transition-colors ${
              tab === t
                ? 'text-teal-400 border-b-2 border-teal-400'
                : 'text-gray-500 hover:text-gray-300'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === 'integrations' && (
        <div className="grid grid-cols-2 gap-3">
          {loading ? (
            <p className="text-gray-500 text-sm col-span-2">Checking connections...</p>
          ) : (
            integrations.map((item) => (
              <div
                key={item.name}
                className="border border-gray-800 rounded-lg p-4 flex items-center gap-3"
              >
                <span className={`w-2.5 h-2.5 rounded-full ${STATUS_COLORS[item.status]}`} />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-200">{item.name}</p>
                  <p className="text-xs text-gray-500 truncate">{item.detail}</p>
                </div>
                <span className="text-xs text-gray-600">{STATUS_LABELS[item.status]}</span>
              </div>
            ))
          )}
        </div>
      )}

      {tab === 'tenants' && (
        <div className="border border-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-500 text-sm">Tenant management coming soon.</p>
        </div>
      )}
    </div>
  );
}
