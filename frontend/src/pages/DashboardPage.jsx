import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { FileText, AlertTriangle, Shield, TrendingUp, RefreshCw, Globe } from 'lucide-react';
import ComplianceScore from '../components/Dashboard/ComplianceScore';
import RiskDistribution from '../components/Dashboard/RiskDistribution';
import ViolationTrends from '../components/Dashboard/ViolationTrends';
import DepartmentRisk from '../components/Dashboard/DepartmentRisk';
import ViolationCard from '../components/Violations/ViolationCard';
import { getDashboardMetrics, getRbiSyncStatus } from '../services/api';
import { useComplianceRefresh } from '../hooks/useComplianceRefresh';

export default function DashboardPage() {
  const [metrics, setMetrics] = useState(null);
  const [rbiStatus, setRbiStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [metricsRes, rbiRes] = await Promise.all([
        getDashboardMetrics(),
        getRbiSyncStatus().catch(() => ({ data: null })),
      ]);
      setMetrics(metricsRes.data);
      setRbiStatus(rbiRes.data);
    } catch (err) {
      setMetrics(null);
      setError(
        err.response?.data?.detail ||
          'Could not load dashboard. Is the backend running on port 8000?'
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  useComplianceRefresh(fetchMetrics);

  const formatTime = (iso) => {
    if (!iso) return 'Never';
    try {
      return new Date(iso).toLocaleString();
    } catch {
      return iso;
    }
  };

  if (loading && !metrics) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-600 border-t-transparent" />
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Compliance Dashboard</h2>
        <div className="rounded-lg border border-danger-200 bg-danger-50 p-4 dark:border-danger-800 dark:bg-danger-900/20">
          <p className="text-sm text-danger-700 dark:text-danger-400">{error}</p>
          <button
            type="button"
            onClick={fetchMetrics}
            className="mt-3 rounded-lg bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const checksPassed = metrics.regulatory_checks_passed ?? 0;
  const checksTotal = metrics.regulatory_checks_total ?? 10;
  const hasIndexedData =
    metrics.total_regulations > 0 || metrics.total_policies > 0;
  const needsAnalysis = hasIndexedData && metrics.total_violations === 0;

  const stats = [
    { label: 'Total Documents', value: metrics.total_documents, icon: FileText, color: 'text-primary-600' },
    { label: 'Violations Found', value: metrics.total_violations, icon: AlertTriangle, color: 'text-danger-600' },
    { label: 'Regulations Indexed', value: metrics.total_regulations, icon: Shield, color: 'text-success-600' },
    { label: 'Policies Indexed', value: metrics.total_policies, icon: TrendingUp, color: 'text-warning-600' },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Compliance Dashboard</h2>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Overview of your regulatory compliance posture
          </p>
        </div>
        <button
          type="button"
          onClick={fetchMetrics}
          disabled={loading}
          className="flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-4 rounded-lg border border-gray-200 bg-white px-4 py-3 text-sm dark:border-gray-700 dark:bg-gray-800">
        <Globe className="h-4 w-4 text-primary-600 dark:text-primary-400" />
        <span className="text-gray-600 dark:text-gray-400">
          RBI last synced: <strong className="text-gray-900 dark:text-white">{formatTime(rbiStatus?.last_sync_at)}</strong>
        </span>
        <Link to="/upload" className="text-primary-600 hover:underline dark:text-primary-400">
          Sync RBI →
        </Link>
      </div>

      {needsAnalysis && (
        <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-900/20">
          <p className="text-sm text-amber-800 dark:text-amber-200">
            Documents are indexed but no analysis has been run yet. Upload your SOP and run{' '}
            <Link to="/analysis" className="font-medium underline">
              Compliance Analysis
            </Link>{' '}
            to see violations and scores.
          </p>
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div
            key={label}
            className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800"
          >
            <div className="flex items-center justify-between">
              <p className="text-sm text-gray-500 dark:text-gray-400">{label}</p>
              <Icon className={`h-5 w-5 ${color}`} />
            </div>
            <p className="mt-2 text-2xl font-bold text-gray-900 dark:text-white">{value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ComplianceScore
          score={metrics.overall_compliance_score}
          checksPassed={checksPassed}
          checksTotal={checksTotal}
        />
        <RiskDistribution data={metrics.risk_distribution} />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <ViolationTrends data={metrics.violation_trends} />
        <DepartmentRisk data={metrics.department_risks} />
      </div>

      {metrics.recent_violations?.length > 0 ? (
        <div>
          <h3 className="mb-3 text-lg font-semibold text-gray-900 dark:text-white">Recent Violations</h3>
          <div className="space-y-3">
            {metrics.recent_violations.slice(0, 5).map((v) => (
              <ViolationCard key={v.violation_id || v.violation_detected} violation={v} />
            ))}
          </div>
          <Link
            to="/violations"
            className="mt-3 inline-block text-sm font-medium text-primary-600 hover:underline dark:text-primary-400"
          >
            View all violations →
          </Link>
        </div>
      ) : (
        !needsAnalysis && (
          <p className="text-center text-sm text-gray-500 dark:text-gray-400">
            No violations recorded. Run analysis after uploading regulations and policies.
          </p>
        )
      )}
    </div>
  );
}
