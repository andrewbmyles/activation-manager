import React, { useEffect } from 'react';
import { ActivationManagerApp } from '../components/ActivationManager/ActivationManagerApp';
import './ActivationManager.css';

export const ActivationManager: React.FC = () => {
  useEffect(() => {
    // Hide the sidebar by adding a class to the body
    document.body.classList.add('activation-manager-active');
    
    return () => {
      // Remove the class when component unmounts
      document.body.classList.remove('activation-manager-active');
    };
  }, []);

  return (
    <div className="activation-manager-fullscreen">
      {/* Full page content area */}
      <div className="activation-manager-full-content">
        {/* Render the full Activation Manager app */}
        <div className="activation-manager-app">
          <ActivationManagerApp />
        </div>
      </div>
    </div>
  );
};