import { useState, useEffect } from 'react';
import { RefreshCw, Globe, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { getRbiSyncStatus, syncRegulations, emitComplianceRefresh } from '../../services/api';

export default function RBISyncPanel() {
  const [status, setStatus] = useState(null);
  const [syncing, setSyncing] = useState(false);
  const [lastResult, setLastResult] = useState(null);
  const [error, setError] = useState(null);

  const loadStatus = async () => {
    try {
      const res = await getRbiSyncStatus();
      setStatus(res.data);
    } catch {
      setStatus(null);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  const handleSync = async () => {
    setSyncing(true);
    setError(null);
    setLastResult(null);
    try {
      const res = await syncRegulations({ max_items: 15 });
      setLastResult(res.data);
      await loadStatus();
      emitComplianceRefresh();
    } catch (err) {
      setError(err.response?.data?.detail || 'RBI sync failed. Check network and backend logs.');
    } finally {
      setSyncing(false);
    }
  };

  const formatTime = (iso) => {
    if (!iso) return 'Never';
    try {
      return new Date(iso).toLocaleString();
    } catch {
      return iso;
    }
  };

  return (
    <div className="rounded-xl border border-primary-200 bg-primary-50/50 p-5 dark:border-primary-900 dark:bg-primary-950/30">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="flex gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100 dark:bg-primary-900/40">
            <Globe className="h-5 w-5 text-primary-600 dark:text-primary-400" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">Live RBI Guidelines Sync</h3>
            <p className="mt-0.5 max-w-xl text-sm text-gray-600 dark:text-gray-400">
              Fetches recent RBI press releases & notifications from official RSS feeds and indexes
              them for policy comparison.
            </p>
            <p className="mt-2 text-xs text-gray-500 dark:text-gray-500">
              Last sync: <span className="font-medium">{formatTime(status?.last_sync_at)}</span>
              {' · '}
              Indexed regulations: <span className="font-medium">{status?.regulations_indexed ?? 0}</span>
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={handleSync}
          disabled={syncing}
          className="flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-primary-700 disabled:opacity-50"
        >
          {syncing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <RefreshCw className="h-4 w-4" />
          )}
          {syncing ? 'Syncing…' : 'Sync RBI Now'}
        </button>
      </div>

      {syncing && (
        <p className="mt-3 text-sm text-primary-700 dark:text-primary-300">
          Downloading from RBI RSS and building embeddings — may take 2–5 minutes…
        </p>
      )}

      {error && (
        <p className="mt-3 flex items-center gap-2 text-sm text-danger-600 dark:text-danger-400">
          <AlertCircle className="h-4 w-4 shrink-0" />
          {error}
        </p>
      )}

      {lastResult && (
        <div className="mt-4 rounded-lg border border-gray-200 bg-white p-3 dark:border-gray-700 dark:bg-gray-800">
          <p className="flex items-center gap-2 text-sm font-medium text-success-700 dark:text-success-400">
            <CheckCircle className="h-4 w-4" />
            Sync complete — {lastResult.new} new, {lastResult.skipped} skipped, {lastResult.failed} failed
          </p>
          {lastResult.items?.length > 0 && (
            <ul className="mt-2 max-h-32 space-y-1 overflow-y-auto text-xs text-gray-600 dark:text-gray-400">
              {lastResult.items.slice(0, 5).map((item, i) => (
                <li key={i} className="truncate">
                  [{item.status}] {item.title}
                  {item.chunks_created ? ` (${item.chunks_created} chunks)` : ''}
                </li>
              ))}
            </ul>
          )}
          <p className="mt-2 text-xs text-primary-700 dark:text-primary-400">
            Next: upload your SOP → run Analysis to compare against live RBI data.
          </p>
        </div>
      )}
    </div>
  );
}
