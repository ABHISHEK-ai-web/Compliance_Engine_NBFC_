import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { Filter, RefreshCw } from 'lucide-react';
import { getViolations } from '../services/api';
import { useComplianceRefresh } from '../hooks/useComplianceRefresh';
import ViolationCard from '../components/Violations/ViolationCard';

export default function ViolationsPage() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState({ severity: '', department: '' });

  const fetchViolations = useCallback(async () => {
    setLoading(true);
    try {
      const params = {};
      if (filter.severity) params.severity = filter.severity;
      if (filter.department) params.department = filter.department;
      const response = await getViolations(params);
      setViolations(response.data);
    } catch {
      setViolations([]);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchViolations();
  }, [fetchViolations]);

  useComplianceRefresh(fetchViolations);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Compliance Violations</h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            All detected compliance gaps and violations
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="rounded-full bg-danger-50 px-3 py-1 text-sm font-medium text-danger-600 dark:bg-danger-500/10 dark:text-danger-500">
            {violations.length} total
          </span>
          <button
            type="button"
            onClick={fetchViolations}
            className="rounded-lg border border-gray-300 p-2 dark:border-gray-600"
            aria-label="Refresh"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Filter className="h-4 w-4 text-gray-400" />
        <select
          value={filter.severity}
          onChange={(e) => setFilter((f) => ({ ...f, severity: e.target.value }))}
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
        >
          <option value="">All Severities</option>
          <option value="CRITICAL">Critical</option>
          <option value="HIGH">High</option>
          <option value="MEDIUM">Medium</option>
          <option value="LOW">Low</option>
        </select>
        <input
          type="text"
          value={filter.department}
          onChange={(e) => setFilter((f) => ({ ...f, department: e.target.value }))}
          placeholder="Filter by department..."
          className="rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white dark:placeholder-gray-500"
        />
      </div>

      {loading ? (
        <div className="flex h-32 items-center justify-center">
          <div className="h-6 w-6 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
        </div>
      ) : violations.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-white p-12 text-center dark:border-gray-700 dark:bg-gray-800">
          <p className="text-gray-500 dark:text-gray-400">
            No violations found.{' '}
            <Link to="/upload" className="text-primary-600 hover:underline dark:text-primary-400">
              Sync RBI
            </Link>
            , upload policy, then{' '}
            <Link to="/analysis" className="text-primary-600 hover:underline dark:text-primary-400">
              run Analysis
            </Link>
            .
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {violations.map((v) => (
            <ViolationCard key={v.violation_id || v.violation_detected} violation={v} />
          ))}
        </div>
      )}
    </div>
  );
}
