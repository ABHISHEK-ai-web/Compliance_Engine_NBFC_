import { useState, useEffect, useCallback } from 'react';
import { getDashboardMetrics, getViolations, runAnalysis } from '../services/api';

export function useDashboard() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getDashboardMetrics();
      setMetrics(response.data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { metrics, loading, error, refresh };
}

export function useViolations(initialFilters = {}) {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState(initialFilters);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const response = await getViolations(filters);
      setViolations(response.data);
    } catch {
      setViolations([]);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetch();
  }, [fetch]);

  return { violations, loading, filters, setFilters, refresh: fetch };
}

export function useAnalysis() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const analyze = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await runAnalysis(params);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  }, []);

  return { result, loading, error, analyze };
}
