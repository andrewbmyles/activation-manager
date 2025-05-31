import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import tobermoryLogo from '../../assets/images/TobermoryLogo.png';
import './Sidebar.css';

interface NavItem {
  id: string;
  title: string;
  path: string;
  active?: boolean;
}

export const Sidebar: React.FC = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const navigation: NavItem[] = [
    {
      id: 'activation-manager',
      title: 'Activation Manager',
      path: '/activation-manager',
      active: true
    }
  ];

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <NavLink to="/home" className="logo-link">
          <img 
            src={tobermoryLogo} 
            alt="Tobermory AI" 
            className="sidebar-logo"
          />
          <h1 className="sidebar-title">
            tobermory<span className="accent">.ai</span>
          </h1>
        </NavLink>
      </div>

      <nav className="sidebar-nav">
        <div className="nav-section">
          <div className="nav-title">Projects</div>
          {navigation.map((item) => (
            item.id === 'activation-manager' ? (
              <a
                key={item.id}
                href="/activation-manager"
                target="_blank"
                rel="noopener noreferrer"
                className="nav-item"
              >
                <div className="nav-icon">
                  {item.active && <span className="status-indicator"></span>}
                </div>
                <span>{item.title}</span>
              </a>
            ) : (
              <NavLink
                key={item.id}
                to={item.path}
                className={({ isActive }) => 
                  `nav-item ${isActive ? 'active' : ''}`
                }
              >
                <div className="nav-icon">
                  {item.active && <span className="status-indicator"></span>}
                </div>
                <span>{item.title}</span>
              </NavLink>
            )
          ))}
        </div>

        <div className="nav-section">
          <div className="nav-title">Resources</div>
          <a href="#" className="nav-item">
            <div className="nav-icon"></div>
            <span>Documentation</span>
          </a>
          <a href="#" className="nav-item">
            <div className="nav-icon"></div>
            <span>API Reference</span>
          </a>
          <a href="#" className="nav-item">
            <div className="nav-icon"></div>
            <span>Team</span>
          </a>
        </div>
      </nav>

      <div className="sidebar-footer">
        <button onClick={handleLogout} className="logout-btn">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
            <path 
              d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4M16 17l5-5-5-5M21 12H9" 
              stroke="currentColor" 
              strokeWidth="2" 
              strokeLinecap="round" 
              strokeLinejoin="round"
            />
          </svg>
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
};