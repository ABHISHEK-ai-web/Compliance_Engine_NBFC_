import { Sun, Moon, Bell } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';

export default function Header() {
  const { darkMode, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-gray-200 bg-white/80 px-6 backdrop-blur-sm dark:border-gray-800 dark:bg-gray-900/80">
      <div>
        <h1 className="text-lg font-semibold text-gray-900 dark:text-white">
          Regulatory Compliance Intelligence Engine
        </h1>
        <p className="text-xs text-gray-500 dark:text-gray-400">
          AI-powered compliance analysis for RBI circulars
        </p>
      </div>
      <div className="flex items-center gap-3">
        <button
          className="relative rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute right-1.5 top-1.5 h-2 w-2 rounded-full bg-danger-500" />
        </button>
        <button
          onClick={toggleTheme}
          className="rounded-lg p-2 text-gray-500 hover:bg-gray-100 dark:text-gray-400 dark:hover:bg-gray-800"
          aria-label="Toggle theme"
        >
          {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </button>
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary-600 text-xs font-medium text-white">
          AC
        </div>
      </div>
    </header>
  );
}
