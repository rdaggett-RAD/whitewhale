export default function PromptStudio() {
  return (
    <div>
      <h2 className="text-xl font-bold text-gray-100 mb-6">Prompt Studio</h2>
      <div className="grid grid-cols-2 gap-4">
        {['Personas', 'Angles', 'Voices', 'Value Props'].map((block) => (
          <div key={block} className="border border-gray-800 rounded-lg p-6">
            <h3 className="text-sm font-bold text-gray-300 mb-2">{block}</h3>
            <p className="text-xs text-gray-500">Manage your {block.toLowerCase()} here.</p>
          </div>
        ))}
      </div>
    </div>
  );
}
