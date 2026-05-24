import { RadialBarChart, RadialBar, ResponsiveContainer } from 'recharts';

export default function ComplianceScore({ score = 0, checksPassed, checksTotal }) {
  const displayScore = Math.min(100, Math.max(0, Number(score) || 0));
  const data = [{ name: 'Score', value: displayScore, fill: getColor(displayScore) }];
  const showChecks =
    typeof checksPassed === 'number' && typeof checksTotal === 'number' && checksTotal > 0;

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Compliance Score</h3>
      <div className="mt-2 flex items-center justify-between">
        <div>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{displayScore.toFixed(1)}%</p>
          <p className={`mt-1 text-sm font-medium ${getTextColor(displayScore)}`}>{getLabel(displayScore)}</p>
          {showChecks && (
            <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
              {checksPassed} of {checksTotal} regulatory checks passed
            </p>
          )}
          {displayScore === 0 && showChecks && checksPassed === 0 && (
            <p className="mt-2 max-w-xs text-xs text-gray-500 dark:text-gray-400">
              Your SOP failed all baseline RBI rule checks. Update policy and re-run analysis.
            </p>
          )}
        </div>
        <div className="h-24 w-24">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%"
              cy="50%"
              innerRadius="70%"
              outerRadius="100%"
              barSize={10}
              data={data}
              startAngle={90}
              endAngle={-270}
            >
              <RadialBar
                background={{ fill: '#e5e7eb' }}
                dataKey="value"
                cornerRadius={5}
                max={100}
              />
            </RadialBarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function getColor(score) {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#f59e0b';
  if (score >= 40) return '#f97316';
  return '#ef4444';
}

function getTextColor(score) {
  if (score >= 80) return 'text-success-600 dark:text-success-500';
  if (score >= 60) return 'text-warning-600 dark:text-warning-500';
  return 'text-danger-600 dark:text-danger-500';
}

function getLabel(score) {
  if (score >= 80) return 'Good Standing';
  if (score >= 60) return 'Needs Attention';
  if (score >= 40) return 'At Risk';
  return 'Critical';
}
