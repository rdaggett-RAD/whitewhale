export default function ActionQueue() {
  return (
    <div>
      <h2 className="text-xl font-bold text-gray-100 mb-6">Action Queue</h2>
      <div className="border border-gray-800 rounded-lg p-8 text-center">
        <p className="text-gray-500 text-sm">No pending actions. Drafts will appear here when signals are processed.</p>
      </div>
    </div>
  );
}
