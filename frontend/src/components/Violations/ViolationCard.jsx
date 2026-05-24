import { AlertTriangle, AlertCircle, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

const severityConfig = {
  CRITICAL: { color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400', icon: AlertCircle, border: 'border-l-red-500' },
  HIGH: { color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400', icon: AlertTriangle, border: 'border-l-orange-500' },
  MEDIUM: { color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400', icon: AlertTriangle, border: 'border-l-yellow-500' },
  LOW: { color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400', icon: Info, border: 'border-l-green-500' },
};

export default function ViolationCard({ violation }) {
  const [expanded, setExpanded] = useState(false);
  const config = severityConfig[violation.severity] || severityConfig.MEDIUM;
  const Icon = config.icon;

  return (
    <div
      className={`rounded-lg border border-l-4 border-gray-200 bg-white p-4 transition-shadow hover:shadow-md dark:border-gray-700 dark:bg-gray-800 ${config.border}`}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start gap-3">
          <Icon className="mt-0.5 h-5 w-5 shrink-0 text-gray-500 dark:text-gray-400" />
          <div>
            <p className="text-sm font-medium text-gray-900 dark:text-white">
              {violation.violation_detected}
            </p>
            <div className="mt-1.5 flex flex-wrap items-center gap-2">
              <span className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${config.color}`}>
                {violation.severity}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">
                {violation.affected_department}
              </span>
              <span className="text-xs text-gray-400 dark:text-gray-500">
                {violation.regulation_reference}
              </span>
            </div>
          </div>
        </div>
        <button
          onClick={() => setExpanded(!expanded)}
          className="shrink-0 rounded p-1 text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
        >
          {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
        </button>
      </div>

      {expanded && (
        <div className="mt-4 space-y-3 border-t border-gray-100 pt-4 dark:border-gray-700">
          <div>
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Missing Requirement</p>
            <p className="mt-0.5 text-sm text-gray-700 dark:text-gray-300">{violation.missing_requirement}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Explanation</p>
            <p className="mt-0.5 text-sm text-gray-700 dark:text-gray-300">{violation.explanation}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Recommendation</p>
            <p className="mt-0.5 text-sm text-primary-700 dark:text-primary-400">{violation.recommendation}</p>
          </div>
          {violation.confidence_score && (
            <div className="flex items-center gap-2">
              <p className="text-xs text-gray-500 dark:text-gray-400">Confidence:</p>
              <div className="h-1.5 w-20 rounded-full bg-gray-200 dark:bg-gray-700">
                <div
                  className="h-1.5 rounded-full bg-primary-500"
                  style={{ width: `${violation.confidence_score * 100}%` }}
                />
              </div>
              <span className="text-xs text-gray-500">{(violation.confidence_score * 100).toFixed(0)}%</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
