import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Upload,
  Search,
  AlertTriangle,
  MessageSquare,
  Shield,
} from 'lucide-react';

const navItems = [
  { path: '/', icon: LayoutDashboard, label: 'Dashboard' },
  { path: '/upload', icon: Upload, label: 'Upload Center' },
  { path: '/analysis', icon: Search, label: 'Analysis' },
  { path: '/violations', icon: AlertTriangle, label: 'Violations' },
  { path: '/audit', icon: MessageSquare, label: 'Audit Assistant' },
];

export default function Sidebar() {
  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-64 border-r border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900 transition-colors">
      <div className="flex h-16 items-center gap-2 border-b border-gray-200 px-6 dark:border-gray-800">
        <Shield className="h-7 w-7 text-primary-600" />
        <span className="text-lg font-bold text-gray-900 dark:text-white">ComplianceAI</span>
      </div>
      <nav className="mt-4 space-y-1 px-3">
        {navItems.map(({ path, icon: Icon, label }) => (
          <NavLink
            key={path}
            to={path}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700 dark:bg-primary-900/20 dark:text-primary-400'
                  : 'text-gray-600 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800'
              }`
            }
          >
            <Icon className="h-5 w-5" />
            {label}
          </NavLink>
        ))}
      </nav>
      <div className="absolute bottom-4 left-0 right-0 px-4">
        <div className="rounded-lg bg-primary-50 p-3 dark:bg-primary-900/20">
          <p className="text-xs font-medium text-primary-800 dark:text-primary-300">
            Regulatory Intelligence
          </p>
          <p className="mt-1 text-xs text-primary-600 dark:text-primary-400">
            Powered by SmolLM + RAG
          </p>
        </div>
      </div>
    </aside>
  );
}
