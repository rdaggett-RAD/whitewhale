export default function SignalFeed() {
  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-100">Signal Feed</h2>
        <button className="px-3 py-1.5 bg-teal-600 hover:bg-teal-500 text-white text-xs rounded transition-colors">
          Run Now
        </button>
      </div>
      <div className="border border-gray-800 rounded-lg p-8 text-center">
        <p className="text-gray-500 text-sm">No signals yet. Run the signal engine or wait for the next scheduled sweep.</p>
      </div>
    </div>
  );
}
