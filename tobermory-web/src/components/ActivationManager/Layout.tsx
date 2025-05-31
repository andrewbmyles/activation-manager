import React from 'react';
import { Users, Monitor, Share2, BarChart3, Home, ChevronDown, Settings, HelpCircle, Target, LogOut, Search } from 'lucide-react';
import clsx from 'clsx';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';

interface LayoutProps {
  onLogout: () => void;
  user: string;
}

export function Layout({ onLogout, user }: LayoutProps) {
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname.split('/')[1] || 'dashboard';
  const [showUserMenu, setShowUserMenu] = React.useState(false);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/dashboard' },
    { id: 'audiences', label: 'Audiences', icon: Users, path: '/audiences' },
    { id: 'variable-picker', label: 'Variable Picker', icon: Search, path: '/variable-picker' },
    { id: 'platforms', label: 'Platforms', icon: Monitor, path: '/platforms' },
    { id: 'distribution', label: 'Distribution', icon: Share2, path: '/distribution' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, path: '/analytics' },
  ];

  // Extract username from email
  const userName = user.split('@')[0].charAt(0).toUpperCase() + user.split('@')[0].slice(1);
  const userInitials = userName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <aside className="w-88 bg-gray-50 border-r border-gray-200 flex flex-col">
        {/* Logo Section */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-md flex items-center justify-center relative overflow-hidden">
              <Target className="text-white" size={24} />
              <div className="absolute inset-0 bg-gradient-to-br from-primary to-primary-hover opacity-30"></div>
            </div>
            <div>
              <h1 className="text-xl font-semibold text-gray-800">Activation Manager</h1>
              <p className="text-xs text-gray-500">Audience Distribution Platform</p>
            </div>
          </div>
        </div>

        {/* User Section */}
        <div className="px-6 py-4 border-b border-gray-200 relative">
          <button 
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="w-full flex items-center justify-between hover:bg-gray-100 p-2 rounded-md transition-colors"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full overflow-hidden bg-primary flex items-center justify-center text-white font-medium">
                {userInitials}
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-800">{userName}</p>
                <p className="text-xs text-gray-500">{user}</p>
              </div>
            </div>
            <ChevronDown size={16} className={clsx("text-gray-400 transition-transform", showUserMenu && "rotate-180")} />
          </button>
          
          {showUserMenu && (
            <div className="absolute top-full left-6 right-6 mt-1 bg-white rounded-md shadow-lg border border-gray-200 z-10">
              <button
                onClick={() => {
                  setShowUserMenu(false);
                  onLogout();
                }}
                className="w-full flex items-center gap-2 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded-md"
              >
                <LogOut size={16} />
                <span>Sign out</span>
              </button>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-4 py-6 overflow-y-auto">
          <div className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPath === item.id || (item.id === 'platforms' && location.pathname.startsWith('/platforms/'));
              return (
                <button
                  key={item.id}
                  onClick={() => navigate(item.path)}
                  className={clsx(
                    'w-full flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium transition-all duration-200',
                    isActive
                      ? 'bg-primary text-white shadow-sm'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-800'
                  )}
                >
                  <Icon size={20} className={isActive ? 'text-white' : 'text-gray-500'} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Bottom Actions */}
        <div className="p-4 border-t border-gray-200 space-y-1">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-800 transition-all duration-200">
            <Settings size={20} className="text-gray-500" />
            <span>Settings</span>
          </button>
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-md text-sm font-medium text-gray-600 hover:bg-gray-100 hover:text-gray-800 transition-all duration-200">
            <HelpCircle size={20} className="text-gray-500" />
            <span>Help & Support</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}