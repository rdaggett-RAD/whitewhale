const TYPE_BADGES = {
  job_posting: { label: 'Hiring', color: 'bg-blue-500/20 text-blue-400' },
  exec_change: { label: 'Exec Move', color: 'bg-purple-500/20 text-purple-400' },
  news_pr: { label: 'News', color: 'bg-amber-500/20 text-amber-400' },
  funding: { label: 'Funding', color: 'bg-emerald-500/20 text-emerald-400' },
  acquisition: { label: 'Acquisition', color: 'bg-red-500/20 text-red-400' },
};

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / 3600000);
  if (hours < 1) return 'just now';
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export default function SignalCard({ signal, onDismiss, onAddWhale }) {
  const badge = TYPE_BADGES[signal.signal_type] || { label: signal.signal_type, color: 'bg-gray-500/20 text-gray-400' };

  return (
    <div className="border border-gray-800 rounded-lg p-4 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-0.5 rounded text-xs font-medium ${badge.color}`}>
              {badge.label}
            </span>
            {signal.urgency_score >= 70 && (
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-500/20 text-red-400">
                High
              </span>
            )}
            {signal.has_connection && (
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-teal-500/20 text-teal-400">
                Connection
              </span>
            )}
            {signal.white_whale_id && (
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-indigo-500/20 text-indigo-400">
                Whale
              </span>
            )}
          </div>

          <p className="text-sm text-gray-200 mb-1">{signal.signal_summary}</p>

          {signal.classification_rationale && (
            <p className="text-xs text-gray-500 mb-2">{signal.classification_rationale}</p>
          )}

          <div className="flex items-center gap-3 text-xs text-gray-600">
            <span>{timeAgo(signal.detected_at)}</span>
            {signal.signal_source && <span>{signal.signal_source}</span>}
            {signal.classification_confidence != null && (
              <span>{signal.classification_confidence}% match</span>
            )}
          </div>
        </div>

        <div className="flex flex-col gap-1 shrink-0">
          {signal.signal_url && (
            <a
              href={signal.signal_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-gray-500 hover:text-teal-400 transition-colors"
            >
              source
            </a>
          )}
          {!signal.white_whale_id && onAddWhale && (
            <button
              onClick={() => onAddWhale(signal)}
              className="text-xs text-gray-500 hover:text-teal-400 transition-colors"
            >
              + whale
            </button>
          )}
          {onDismiss && signal.status === 'new' && (
            <button
              onClick={() => onDismiss(signal.id)}
              className="text-xs text-gray-500 hover:text-red-400 transition-colors"
            >
              dismiss
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
