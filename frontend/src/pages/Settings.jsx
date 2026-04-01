export default function Settings() {
  return (
    <div>
      <h2 className="text-xl font-bold text-gray-100 mb-6">Settings</h2>
      <div className="space-y-4">
        <div className="border border-gray-800 rounded-lg p-6">
          <h3 className="text-sm font-bold text-gray-300 mb-2">ICP Configuration</h3>
          <p className="text-xs text-gray-500">Industries, company stages, employee range, geos, signal preferences.</p>
        </div>
        <div className="border border-gray-800 rounded-lg p-6">
          <h3 className="text-sm font-bold text-gray-300 mb-2">Delivery Settings</h3>
          <p className="text-xs text-gray-500">Digest frequency, from-address, auto-approve preferences.</p>
        </div>
      </div>
    </div>
  );
}
