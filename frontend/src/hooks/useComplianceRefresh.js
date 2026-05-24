import { useEffect } from 'react';

/** Re-fetch when sync/analysis completes elsewhere in the app */
export function useComplianceRefresh(onRefresh) {
  useEffect(() => {
    const handler = () => onRefresh?.();
    window.addEventListener('compliance:refresh', handler);
    return () => window.removeEventListener('compliance:refresh', handler);
  }, [onRefresh]);
}
