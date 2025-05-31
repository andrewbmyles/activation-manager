import React from 'react';
import { ProjectCard } from '../components/Projects/ProjectCard';
import './Home.css';

export const Home: React.FC = () => {

  const handleProjectClick = () => {
    // Navigate to Activation Manager
    window.location.href = '/activation-manager';
  };

  return (
    <div className="home-page fade-in">
      <div className="home-header">
        <h2>Welcome back</h2>
        <p>Continue where you left off or start something new</p>
      </div>

      <section className="projects-section">
        <h3>Recent Projects</h3>
        
        <div className="projects-grid">
          <ProjectCard
            title="Activation Manager"
            description="Manage and track activation processes with advanced monitoring and analytics capabilities."
            status="active"
            lastUpdated="Updated 2 hours ago"
            progress="In Progress"
            onClick={handleProjectClick}
          />
        </div>
      </section>

      {/* Floating Action Button */}
      <button className="fab" title="Create new project">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
          <path 
            d="M12 5v14M5 12h14" 
            stroke="currentColor" 
            strokeWidth="2" 
            strokeLinecap="round"
          />
        </svg>
      </button>
    </div>
  );
};