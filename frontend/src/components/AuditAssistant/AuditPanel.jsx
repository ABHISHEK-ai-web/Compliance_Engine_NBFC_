import { useState } from 'react';
import { Send, Bot, User, Loader2, FileText } from 'lucide-react';
import { queryAudit } from '../../services/api';

export default function AuditPanel() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'I am your regulatory compliance assistant. Ask me about RBI guidelines, compliance requirements, or policy gaps.',
      sources: [],
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const question = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: question }]);
    setLoading(true);

    try {
      const response = await queryAudit(question);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.data.answer,
          sources: response.data.sources || [],
          confidence: response.data.confidence,
        },
      ]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error processing your query. Please ensure documents are uploaded first.',
          sources: [],
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const sampleQueries = [
    'What are the KFS requirements under RBI Digital Lending?',
    'Does our SOP cover the cooling-off period provision?',
    'What grievance redressal mechanisms are mandated?',
    'Are there data privacy gaps in our current policy?',
  ];

  return (
    <div className="flex h-[calc(100vh-10rem)] flex-col rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
      <div className="border-b border-gray-200 px-6 py-4 dark:border-gray-700">
        <h3 className="font-semibold text-gray-900 dark:text-white">Compliance Audit Assistant</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Ask questions about regulatory requirements and policy compliance
        </p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-6">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : ''}`}>
            {msg.role === 'assistant' && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-100 dark:bg-primary-900/30">
                <Bot className="h-4 w-4 text-primary-600 dark:text-primary-400" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-lg px-4 py-3 ${
                msg.role === 'user'
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
              }`}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div className="mt-3 space-y-1 border-t border-gray-200 pt-2 dark:border-gray-600">
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Sources:</p>
                  {msg.sources.map((src, j) => (
                    <div key={j} className="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                      <FileText className="h-3 w-3" />
                      <span>{src.filename} (p.{src.page})</span>
                      <span className="ml-auto text-primary-600 dark:text-primary-400">
                        {(src.relevance * 100).toFixed(0)}% match
                      </span>
                    </div>
                  ))}
                </div>
              )}
              {msg.confidence !== undefined && msg.confidence > 0 && (
                <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">
                  Confidence: {(msg.confidence * 100).toFixed(0)}%
                </p>
              )}
            </div>
            {msg.role === 'user' && (
              <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gray-200 dark:bg-gray-600">
                <User className="h-4 w-4 text-gray-600 dark:text-gray-300" />
              </div>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary-100 dark:bg-primary-900/30">
              <Bot className="h-4 w-4 text-primary-600 dark:text-primary-400" />
            </div>
            <div className="flex items-center gap-2 rounded-lg bg-gray-100 px-4 py-3 dark:bg-gray-700">
              <Loader2 className="h-4 w-4 animate-spin text-primary-500" />
              <span className="text-sm text-gray-500 dark:text-gray-400">Analyzing...</span>
            </div>
          </div>
        )}
      </div>

      {messages.length <= 1 && (
        <div className="border-t border-gray-200 px-6 py-3 dark:border-gray-700">
          <p className="mb-2 text-xs text-gray-500 dark:text-gray-400">Try asking:</p>
          <div className="flex flex-wrap gap-2">
            {sampleQueries.map((q, i) => (
              <button
                key={i}
                onClick={() => setInput(q)}
                className="rounded-full bg-gray-100 px-3 py-1 text-xs text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="border-t border-gray-200 p-4 dark:border-gray-700">
        <div className="flex items-center gap-3">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about compliance requirements..."
            className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:placeholder-gray-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="rounded-lg bg-primary-600 p-2.5 text-white hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </form>
    </div>
  );
}
