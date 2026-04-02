const STATUS_COLORS = {
  cold: 'text-blue-400',
  warming: 'text-amber-400',
  active: 'text-emerald-400',
  won: 'text-teal-400',
  lost: 'text-red-400',
  paused: 'text-gray-500',
};

const TIER_LABELS = {
  1: { label: 'T1', color: 'bg-red-500/20 text-red-400' },
  2: { label: 'T2', color: 'bg-amber-500/20 text-amber-400' },
  3: { label: 'T3', color: 'bg-gray-500/20 text-gray-400' },
};

function timeAgo(dateStr) {
  if (!dateStr) return 'never';
  const diff = Date.now() - new Date(dateStr).getTime();
  const days = Math.floor(diff / 86400000);
  if (days < 1) return 'today';
  if (days === 1) return 'yesterday';
  return `${days}d ago`;
}

export default function WhaleCard({ whale, onClick }) {
  const tier = TIER_LABELS[whale.priority_tier] || TIER_LABELS[2];
  const statusColor = STATUS_COLORS[whale.status] || 'text-gray-400';

  return (
    <div
      onClick={() => onClick?.(whale)}
      className="border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-colors cursor-pointer"
    >
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className={`px-1.5 py-0.5 rounded text-xs font-bold ${tier.color}`}>
            {tier.label}
          </span>
          <h3 className="text-sm font-medium text-gray-200">{whale.company_name}</h3>
        </div>
        <span className={`text-xs capitalize ${statusColor}`}>{whale.status}</span>
      </div>

      {whale.domain && (
        <p className="text-xs text-gray-500 mb-2">{whale.domain}</p>
      )}

      {whale.why_they_matter && (
        <p className="text-xs text-gray-400 mb-2 line-clamp-2">{whale.why_they_matter}</p>
      )}

      <div className="flex items-center gap-3 text-xs text-gray-600">
        <span>Last signal: {timeAgo(whale.last_signal_at)}</span>
        {whale.ideal_entry_point && <span>Target: {whale.ideal_entry_point}</span>}
      </div>
    </div>
  );
}
