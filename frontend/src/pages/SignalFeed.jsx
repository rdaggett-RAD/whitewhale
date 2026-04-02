import { useState, useEffect } from 'react';
import api from '../api/client';
import SignalCard from '../components/SignalCard';

const SIGNAL_TYPES = ['all', 'job_posting', 'exec_change', 'news_pr', 'funding', 'acquisition'];

export default function SignalFeed() {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [filter, setFilter] = useState('all');

  const fetchSignals = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter !== 'all') params.signal_type = filter;
      const res = await api.get('/signals', { params });
      setSignals(res.data);
    } catch {
      setSignals([]);
    }
    setLoading(false);
  };

  useEffect(() => { fetchSignals(); }, [filter]);

  const handleRun = async () => {
    setRunning(true);
    try {
      await api.post('/signals/run');
      await fetchSignals();
    } catch { /* ignore */ }
    setRunning(false);
  };

  const handleDismiss = async (signalId) => {
    try {
      await api.patch(`/signals/${signalId}/status`, { status: 'dismissed' });
      setSignals((prev) => prev.filter((s) => s.id !== signalId));
    } catch { /* ignore */ }
  };

  const handleAddWhale = async (signal) => {
    try {
      await api.post('/whales', {
        company_name: signal.signal_summary.split(' ')[0] || 'Unknown',
        domain: null,
      });
    } catch { /* ignore */ }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-100">Signal Feed</h2>
        <button
          onClick={handleRun}
          disabled={running}
          className="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 disabled:bg-gray-700 text-white text-xs rounded transition-colors"
        >
          {running ? 'Running...' : 'Run Now'}
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        {SIGNAL_TYPES.map((type) => (
          <button
            key={type}
            onClick={() => setFilter(type)}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              filter === type
                ? 'bg-teal-600 text-white'
                : 'bg-gray-900 text-gray-400 hover:text-gray-200'
            }`}
          >
            {type === 'all' ? 'All' : type.replace('_', ' ')}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-gray-500 text-sm">Loading signals...</p>
      ) : signals.length === 0 ? (
        <div className="border border-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-500 text-sm">
            No signals yet. Run the signal engine or wait for the next scheduled sweep.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {signals.map((signal) => (
            <SignalCard
              key={signal.id}
              signal={signal}
              onDismiss={handleDismiss}
              onAddWhale={handleAddWhale}
            />
          ))}
        </div>
      )}
    </div>
  );
}
