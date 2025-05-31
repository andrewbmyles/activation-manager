import React from 'react';
import './ProjectCard.css';

interface ProjectCardProps {
  title: string;
  description: string;
  status: 'active' | 'pending' | 'completed';
  lastUpdated: string;
  progress?: string;
  onClick?: () => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  title,
  description,
  status,
  lastUpdated,
  progress,
  onClick
}) => {
  return (
    <div className="project-card" onClick={onClick}>
      <span className={`project-status status-${status}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
      
      <h4 className="project-title">{title}</h4>
      <p className="project-description">{description}</p>
      
      <div className="project-meta">
        <span>{lastUpdated}</span>
        {progress && <span>{progress}</span>}
      </div>
    </div>
  );
};