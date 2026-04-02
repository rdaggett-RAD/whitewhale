import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const navItems = [
  { to: '/', label: 'Signal Feed', icon: '>' },
  { to: '/whales', label: 'White Whales', icon: '#' },
  { to: '/actions', label: 'Action Queue', icon: '!' },
  { to: '/prompts', label: 'Prompt Studio', icon: '*' },
  { to: '/settings', label: 'Settings', icon: '~' },
  { to: '/admin', label: 'Admin', icon: '@' },
];

export default function Sidebar() {
  const { user, logout } = useAuth();

  return (
    <aside className="w-56 min-h-screen bg-gray-950 border-r border-gray-800 flex flex-col">
      <div className="p-4 border-b border-gray-800">
        <h1 className="text-lg font-bold text-teal-400 tracking-tight">WHITE WHALE</h1>
        <p className="text-xs text-gray-500 mt-1">signal intelligence</p>
      </div>

      <nav className="flex-1 py-4">
        {navItems.map(({ to, label, icon }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-2 text-sm transition-colors ${
                isActive
                  ? 'text-teal-400 bg-gray-900 border-r-2 border-teal-400'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-900/50'
              }`
            }
          >
            <span className="text-xs font-mono w-4">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {user && (
        <div className="p-4 border-t border-gray-800">
          <p className="text-xs text-gray-500 truncate">{user.email}</p>
          <button
            onClick={logout}
            className="text-xs text-gray-600 hover:text-red-400 mt-1 transition-colors"
          >
            logout
          </button>
        </div>
      )}
    </aside>
  );
}
