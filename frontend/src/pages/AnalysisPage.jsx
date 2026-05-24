import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, Loader2, AlertTriangle } from 'lucide-react';
import { runAnalysis, emitComplianceRefresh } from '../services/api';
import ViolationCard from '../components/Violations/ViolationCard';
import ComplianceScore from '../components/Dashboard/ComplianceScore';

export default function AnalysisPage() {
  const [query, setQuery] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await runAnalysis({ query: query || undefined });
      setResult(response.data);
      emitComplianceRefresh();
    } catch (err) {
      const msg = err.code === 'ECONNABORTED'
        ? 'Analysis timed out. Try USE_SLM=false in backend .env for faster rule-only analysis.'
        : err.response?.data?.detail || 'Analysis failed. Sync RBI + upload policy PDF first.';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Compliance Gap Analysis</h2>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Compare live RBI guidelines against your internal policies
        </p>
      </div>

      <div className="rounded-lg border border-gray-200 bg-gray-50 p-4 text-sm text-gray-600 dark:border-gray-700 dark:bg-gray-800/50 dark:text-gray-400">
        <strong className="text-gray-800 dark:text-gray-200">Before you start:</strong>{' '}
        <Link to="/upload" className="text-primary-600 hover:underline dark:text-primary-400">
          Sync RBI
        </Link>{' '}
        → upload internal SOP → Analyze (first run may take 1–5 min if AI model is enabled).
      </div>

      <form onSubmit={handleAnalyze} className="flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Focus area (optional): e.g. digital lending, KYC, grievance"
          disabled={loading}
          className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm text-gray-900 placeholder-gray-400 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500 disabled:opacity-60 dark:border-gray-600 dark:bg-gray-800 dark:text-white"
        />
        <button
          type="submit"
          disabled={loading}
          className="flex items-center justify-center gap-2 rounded-lg bg-primary-600 px-6 py-2.5 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </form>

      {loading && (
        <div className="rounded-lg border border-primary-200 bg-primary-50 p-4 text-sm text-primary-800 dark:border-primary-800 dark:bg-primary-950/40 dark:text-primary-200">
          Running rule engine + RAG retrieval
          {query ? ` for "${query}"` : ''}. Please wait…
        </div>
      )}

      {error && (
        <div className="flex items-start gap-2 rounded-lg bg-danger-50 p-4 text-danger-600 dark:bg-danger-500/10 dark:text-danger-500">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
          <p className="text-sm">{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            <ComplianceScore
              score={result.compliance_score}
              checksPassed={result.regulatory_checks_passed}
              checksTotal={result.regulatory_checks_total}
            />
            <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800 lg:col-span-2">
              <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Summary</h3>
              <p className="mt-2 text-sm text-gray-800 dark:text-gray-200">{result.summary}</p>
              <div className="mt-4 flex flex-wrap gap-3 text-sm">
                <span className="rounded-full bg-red-100 px-2 py-0.5 text-red-800 dark:bg-red-900/30 dark:text-red-300">
                  Critical: {result.critical_count}
                </span>
                <span className="rounded-full bg-orange-100 px-2 py-0.5 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300">
                  High: {result.high_count}
                </span>
                <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300">
                  Medium: {result.medium_count}
                </span>
                <span className="rounded-full bg-gray-100 px-2 py-0.5 text-gray-800 dark:bg-gray-700 dark:text-gray-300">
                  Low: {result.low_count}
                </span>
              </div>
            </div>
          </div>

          <div className="space-y-3">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Findings ({result.violations.length})
            </h3>
            {result.violations.map((v) => (
              <ViolationCard key={v.violation_id} violation={v} />
            ))}
          </div>

          <p className="text-sm text-gray-500 dark:text-gray-400">
            <Link to="/" className="text-primary-600 hover:underline dark:text-primary-400">
              View updated dashboard →
            </Link>
          </p>
        </div>
      )}
    </div>
  );
}
