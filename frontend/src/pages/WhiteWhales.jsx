import { useState, useEffect } from 'react';
import api from '../api/client';
import WhaleCard from '../components/WhaleCard';

export default function WhiteWhales() {
  const [whales, setWhales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [selected, setSelected] = useState(null);
  const [form, setForm] = useState({
    company_name: '', domain: '', why_they_matter: '',
    ideal_entry_point: '', priority_tier: 2,
  });

  const fetchWhales = async () => {
    setLoading(true);
    try {
      const res = await api.get('/whales');
      setWhales(res.data);
    } catch { setWhales([]); }
    setLoading(false);
  };

  useEffect(() => { fetchWhales(); }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/whales', form);
      setShowForm(false);
      setForm({ company_name: '', domain: '', why_they_matter: '', ideal_entry_point: '', priority_tier: 2 });
      await fetchWhales();
    } catch { /* ignore */ }
  };

  const handleStatusChange = async (whaleId, status) => {
    try {
      await api.patch(`/whales/${whaleId}`, { status });
      setSelected(null);
      await fetchWhales();
    } catch { /* ignore */ }
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-100">White Whales</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white text-xs rounded transition-colors"
        >
          {showForm ? 'Cancel' : '+ Add Whale'}
        </button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="border border-gray-800 rounded-lg p-4 mb-6 space-y-3">
          <input
            placeholder="Company name *"
            value={form.company_name}
            onChange={(e) => setForm({ ...form, company_name: e.target.value })}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded text-sm text-gray-200 focus:border-teal-500 focus:outline-none"
            required
          />
          <input
            placeholder="Domain (e.g. company.com)"
            value={form.domain}
            onChange={(e) => setForm({ ...form, domain: e.target.value })}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded text-sm text-gray-200 focus:border-teal-500 focus:outline-none"
          />
          <input
            placeholder="Why they matter"
            value={form.why_they_matter}
            onChange={(e) => setForm({ ...form, why_they_matter: e.target.value })}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded text-sm text-gray-200 focus:border-teal-500 focus:outline-none"
          />
          <input
            placeholder="Ideal entry point (e.g. VP RevOps)"
            value={form.ideal_entry_point}
            onChange={(e) => setForm({ ...form, ideal_entry_point: e.target.value })}
            className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded text-sm text-gray-200 focus:border-teal-500 focus:outline-none"
          />
          <div className="flex items-center gap-3">
            <label className="text-xs text-gray-400">Priority:</label>
            {[1, 2, 3].map((t) => (
              <button
                key={t}
                type="button"
                onClick={() => setForm({ ...form, priority_tier: t })}
                className={`px-2 py-1 text-xs rounded ${
                  form.priority_tier === t ? 'bg-teal-600 text-white' : 'bg-gray-900 text-gray-400'
                }`}
              >
                Tier {t}
              </button>
            ))}
          </div>
          <button
            type="submit"
            className="px-4 py-2 bg-teal-600 hover:bg-teal-500 text-white text-xs rounded transition-colors"
          >
            Add Whale
          </button>
        </form>
      )}

      {/* Detail panel */}
      {selected && (
        <div className="border border-teal-800 rounded-lg p-4 mb-6 bg-gray-900/50">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-gray-200">{selected.company_name}</h3>
            <button onClick={() => setSelected(null)} className="text-xs text-gray-500 hover:text-gray-300">close</button>
          </div>
          {selected.why_they_matter && <p className="text-xs text-gray-400 mb-2">{selected.why_they_matter}</p>}
          {selected.internal_notes && <p className="text-xs text-gray-500 mb-3">{selected.internal_notes}</p>}
          <div className="flex gap-2">
            {['cold', 'warming', 'active', 'won', 'lost', 'paused'].map((s) => (
              <button
                key={s}
                onClick={() => handleStatusChange(selected.id, s)}
                className={`px-2 py-1 text-xs rounded capitalize ${
                  selected.status === s ? 'bg-teal-600 text-white' : 'bg-gray-800 text-gray-400 hover:text-gray-200'
                }`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {loading ? (
        <p className="text-gray-500 text-sm">Loading whales...</p>
      ) : whales.length === 0 ? (
        <div className="border border-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-500 text-sm">No target accounts pinned yet. Add your first White Whale to start tracking.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {whales.map((whale) => (
            <WhaleCard key={whale.id} whale={whale} onClick={setSelected} />
          ))}
        </div>
      )}
    </div>
  );
}
