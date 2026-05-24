import AuditPanel from '../components/AuditAssistant/AuditPanel';

export default function AuditPage() {
  return (
    <div>
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Audit Assistant</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Query the compliance knowledge base with natural language
        </p>
      </div>
      <AuditPanel />
    </div>
  );
}
