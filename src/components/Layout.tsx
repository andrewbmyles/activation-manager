import React from 'react';
import { Users, Monitor, Share2, BarChart3, Home, ChevronDown, Settings, HelpCircle, Target } from 'lucide-react';
import { clsx } from 'clsx';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';

export function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const currentPath = location.pathname.split('/')[1] || 'dashboard';

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home, path: '/dashboard' },
    { id: 'audiences', label: 'Audiences', icon: Users, path: '/audiences' },
    { id: 'platforms', label: 'Platforms', icon: Monitor, path: '/platforms' },
    { id: 'distribution', label: 'Distribution', icon: Share2, path: '/distribution' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, path: '/analytics' },
  ];

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
        <div className="px-6 py-4 border-b border-gray-200">
          <button className="w-full flex items-center justify-between hover:bg-gray-100 p-2 rounded-md transition-colors">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full overflow-hidden bg-gray-300">
                <img 
                  src="/headshot.jpg" 
                  alt="Andrew Myles" 
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    e.currentTarget.parentElement!.innerHTML = '<span class="text-white text-sm font-medium flex items-center justify-center w-full h-full bg-primary">AM</span>';
                  }}
                />
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-800">Andrew Myles</p>
                <p className="text-xs text-gray-500">Admin</p>
              </div>
            </div>
            <ChevronDown size={16} className="text-gray-400" />
          </button>
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